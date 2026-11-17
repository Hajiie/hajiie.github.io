"""CPU에서 MNIST를 MLP 또는 CNN으로 학습하고 CSV·HTML 결과를 저장합니다."""
import argparse
import csv
import html
import json
import random
from pathlib import Path


def build_model(torch, name, classes):
    nn = torch.nn
    if name == "mlp":
        return nn.Sequential(nn.Flatten(), nn.Linear(28 * 28, 64), nn.ReLU(), nn.Linear(64, classes))
    return nn.Sequential(
        nn.Conv2d(1, 8, kernel_size=3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
        nn.Conv2d(8, 16, kernel_size=3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
        nn.Flatten(), nn.Linear(16 * 7 * 7, classes),
    )


def synthetic_dataset(torch, count, seed):
    """네트워크 없는 동작 확인용. MNIST 성능 평가를 대신하지 않습니다."""
    generator = torch.Generator().manual_seed(seed)
    images = torch.rand(count, 1, 28, 28, generator=generator) * 0.1
    labels = torch.arange(count) % 2
    for index, label in enumerate(labels):
        offset = int(torch.randint(7, 19, (1,), generator=generator))
        if int(label) == 0:
            images[index, 0, 4:24, offset:offset + 3] = 1
        else:
            images[index, 0, offset:offset + 3, 4:24] = 1
    return torch.utils.data.TensorDataset(images, labels)


def load_datasets(torch, args):
    if args.dataset == "synthetic":
        return (synthetic_dataset(torch, args.train_limit, args.seed),
                synthetic_dataset(torch, args.validation_limit, args.seed + 1),
                synthetic_dataset(torch, args.test_limit, args.seed + 2), 2)
    from torchvision import datasets, transforms
    transform = transforms.ToTensor()
    train = datasets.MNIST(str(args.data_dir), train=True, download=True, transform=transform)
    test = datasets.MNIST(str(args.data_dir), train=False, download=True, transform=transform)
    generator = torch.Generator().manual_seed(args.seed)
    indices = torch.randperm(len(train), generator=generator)
    train_indices = indices[:args.train_limit].tolist()
    validation_indices = indices[args.train_limit:args.train_limit + args.validation_limit].tolist()
    test_indices = torch.randperm(len(test), generator=generator)[:args.test_limit].tolist()
    return (torch.utils.data.Subset(train, train_indices), torch.utils.data.Subset(train, validation_indices),
            torch.utils.data.Subset(test, test_indices), 10)


def evaluate(torch, model, loader, criterion):
    model.eval()
    total_loss, correct, total = 0.0, 0, 0
    with torch.no_grad():
        for images, labels in loader:
            logits = model(images)
            total_loss += criterion(logits, labels).item() * labels.numel()
            correct += int((logits.argmax(1) == labels).sum())
            total += labels.numel()
    return total_loss / total, correct / total


def write_report(torch, args, model, validation, test, history, classes, final_test):
    samples = test if final_test else validation
    report_split = "test" if final_test else "validation"
    args.out.mkdir(parents=True, exist_ok=True)
    with (args.out / "metrics.csv").open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(history[0]))
        writer.writeheader()
        writer.writerows(history)
    model.eval()
    predictions, tiles = [], []
    with torch.no_grad():
        for index in range(min(12, len(samples))):
            image, label = samples[index]
            probabilities = model(image.unsqueeze(0)).softmax(1)[0]
            predicted = int(probabilities.argmax())
            predictions.append({"index": index, "label": int(label), "predicted": predicted, "probabilities": probabilities.tolist()})
            rectangles = []
            for y in range(28):
                for x in range(28):
                    gray = round(float(image[0, y, x].clamp(0, 1)) * 255)
                    rectangles.append(f'<rect x="{x}" y="{y}" width="1" height="1" fill="rgb({gray},{gray},{gray})"/>')
            tiles.append(f'<figure><svg viewBox="0 0 28 28" role="img" aria-label="Test image {index}">{"".join(rectangles)}</svg><figcaption>정답 {int(label)} / 예측 {predicted}</figcaption></figure>')
    payload = {"model": args.model, "dataset": args.dataset, "classes": classes, "seed": args.seed,
               "train_samples": args.train_limit, "validation_samples": args.validation_limit, "test_samples": args.test_limit,
               "test_evaluated": final_test is not None, "final_test": final_test, "prediction_split": report_split,
               "torch_version": torch.__version__, "device": "cpu", "metrics": history, "predictions": predictions}
    (args.out / "results.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    torch.save(model.state_dict(), args.out / "weights.pt")
    last = history[-1]
    score = final_test if final_test else {"loss": last["validation_loss"], "accuracy": last["validation_accuracy"]}
    report = f'''<!doctype html><html lang="ko"><meta charset="utf-8"><title>연구실 AI 실습 결과</title>
<style>body{{font:16px system-ui;max-width:960px;margin:40px auto;padding:16px;color:#162033}}main{{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:16px}}figure{{margin:0;padding:16px;background:#edf1f7;border-radius:12px}}svg{{width:100%;image-rendering:pixelated}}figcaption{{margin-top:10px;font-size:14px}}</style>
<h1>{html.escape(args.model.upper())} · {html.escape(args.dataset)} 실습 결과</h1>
<p>CPU / train {args.train_limit}개 / validation {args.validation_limit}개 / test {args.test_limit}개 / seed {args.seed}</p>
<p>{report_split} 정확도 {score['accuracy']:.1%} · loss {score['loss']:.4f}</p>
<p>소규모 실습 결과입니다. 데이터 수·seed·학습 조건이 다르면 결과가 달라집니다.</p>
<main>{''.join(tiles)}</main></html>'''
    (args.out / "report.html").write_text(report, encoding="utf-8")
    return payload


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=("mlp", "cnn"), default="cnn")
    parser.add_argument("--dataset", choices=("mnist", "synthetic"), default="mnist")
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--train-limit", type=int, default=2000)
    parser.add_argument("--validation-limit", type=int, default=500)
    parser.add_argument("--evaluate-test", action="store_true", help="조건을 확정한 뒤 최종 test를 한 번 평가")
    parser.add_argument("--test-limit", type=int, default=500)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--lr", type=float, default=0.001)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--out", type=Path, default=Path("results/cnn"))
    args = parser.parse_args(argv)
    if not (1 <= args.epochs <= 20 and 1 <= args.train_limit <= 60000 and 1 <= args.validation_limit <= 5000 and args.train_limit + args.validation_limit <= 60000 and 1 <= args.test_limit <= 10000 and 1 <= args.batch_size <= 256 and 0 < args.lr <= 0.1):
        parser.error("epochs 1..20, train-limit 1..60000, validation-limit 1..5000 (train+validation <=60000), test-limit 1..10000, batch-size 1..256, lr (0, 0.1] 범위로 설정")
    try:
        import torch
    except ImportError as error:
        raise SystemExit("먼저 README의 PyTorch 설치 단계를 실행하세요") from error
    random.seed(args.seed)
    torch.manual_seed(args.seed)
    torch.set_num_threads(min(4, torch.get_num_threads()))
    torch.use_deterministic_algorithms(True)
    train, validation, test, classes = load_datasets(torch, args)
    loader = torch.utils.data.DataLoader(train, batch_size=args.batch_size, shuffle=True,
                                       generator=torch.Generator().manual_seed(args.seed), num_workers=0)
    validation_loader = torch.utils.data.DataLoader(validation, batch_size=args.batch_size, shuffle=False, num_workers=0)
    model = build_model(torch, args.model, classes).to("cpu")
    criterion = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    history = []
    for epoch in range(1, args.epochs + 1):
        model.train()
        total_loss, total = 0.0, 0
        for images, labels in loader:
            optimizer.zero_grad()
            logits = model(images)
            loss = criterion(logits, labels)  # raw logits 사용: softmax를 먼저 적용하지 않음
            loss.backward()
            optimizer.step()
            total_loss += loss.item() * labels.numel()
            total += labels.numel()
        validation_loss, accuracy = evaluate(torch, model, validation_loader, criterion)
        row = {"epoch": epoch, "train_loss": total_loss / total, "validation_loss": validation_loss, "validation_accuracy": accuracy}
        history.append(row)
        print(f"epoch {epoch}: train loss={row['train_loss']:.4f}, validation loss={validation_loss:.4f}, validation accuracy={accuracy:.1%}")
    final_test = None
    if args.evaluate_test:
        test_loader = torch.utils.data.DataLoader(test, batch_size=args.batch_size, shuffle=False, num_workers=0)
        loss, accuracy = evaluate(torch, model, test_loader, criterion)
        final_test = {"loss": loss, "accuracy": accuracy}
    result = write_report(torch, args, model, validation, test, history, classes, final_test)
    print(f"결과: {(args.out / 'report.html').resolve()}")
    return result


if __name__ == "__main__":
    main()
