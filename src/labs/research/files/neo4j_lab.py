"""연구 협업 그래프: ZIP을 푼 폴더에서 seed -> queries 순서로 실행합니다."""
import argparse
import csv
import getpass
import json
import os
from pathlib import Path

LAB_ID = "research-lab-v1"
LABELS = ("Researcher", "Topic", "Paper")
RELATIONSHIPS = ("WORKS_ON", "AUTHORED", "ABOUT", "COLLABORATES_WITH")
QUERIES = {
    "topics": """MATCH (r:ResearchLab:Researcher {lab_id: $lab})
                  -[:WORKS_ON]->(t:ResearchLab:Topic {lab_id: $lab})
                  RETURN r.name AS researcher, t.name AS topic ORDER BY researcher""",
    "shared": """MATCH (a:ResearchLab:Researcher {lab_id: $lab})
                  -[:WORKS_ON]->(t:ResearchLab:Topic {lab_id: $lab})
                  <-[:WORKS_ON]-(b:ResearchLab:Researcher {lab_id: $lab})
                  WHERE a.id < b.id
                  RETURN a.name AS researcher_a, b.name AS researcher_b, t.name AS topic
                  ORDER BY researcher_a, researcher_b""",
    "path": """MATCH (a:ResearchLab {lab_id: $lab, id: 'minji'}),
                (b:ResearchLab {lab_id: $lab, id: 'sora'})
                MATCH p = shortestPath((a)-[*1..6]-(b))
                WHERE all(n IN nodes(p) WHERE n:ResearchLab AND n.lab_id = $lab)
                RETURN [n IN nodes(p) | n.name] AS path, length(p) AS hops""",
}


def seed_transaction(tx, graph):
    for label in LABELS:
        rows = [{"id": n["id"], "name": n["name"]} for n in graph["nodes"] if n["label"] == label]
        # label/type은 사용자 입력 대신 위의 고정 허용 목록에서만 선택합니다.
        tx.run(f"""UNWIND $rows AS row
                   MERGE (n:ResearchLab:{label} {{lab_id: $lab, id: row.id}})
                   SET n.name = row.name""", rows=rows, lab=LAB_ID).consume()
    for relationship in RELATIONSHIPS:
        rows = [e for e in graph["edges"] if e["type"] == relationship]
        tx.run(f"""UNWIND $rows AS row
                   MATCH (a:ResearchLab {{lab_id: $lab, id: row.source}})
                   MATCH (b:ResearchLab {{lab_id: $lab, id: row.target}})
                   MERGE (a)-[:{relationship}]->(b)""", rows=rows, lab=LAB_ID).consume()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("seed", "queries", "reset"))
    parser.add_argument("--uri", default=os.getenv("NEO4J_URI", "bolt://127.0.0.1:17687"))
    parser.add_argument("--user", default="neo4j")
    parser.add_argument("--database", default="neo4j")
    parser.add_argument("--out", type=Path, default=Path("results/neo4j"))
    parser.add_argument("--confirm", help="reset에는 research-lab-v1을 명시해야 합니다")
    args = parser.parse_args(argv)
    if args.action == "reset" and args.confirm != LAB_ID:
        parser.error("실습 데이터 삭제: reset --confirm research-lab-v1")
    try:
        from neo4j import GraphDatabase
    except ImportError as error:
        raise SystemExit("먼저 python -m pip install -r requirements-neo4j.txt 실행") from error
    password = os.getenv("NEO4J_PASSWORD") or getpass.getpass("Neo4j password: ")
    with GraphDatabase.driver(args.uri, auth=(args.user, password)) as driver:
        driver.verify_connectivity()
        if args.action == "seed":
            graph = json.loads(Path(__file__).with_name("graph.json").read_text(encoding="utf-8"))
            if graph["labId"] != LAB_ID:
                raise ValueError("실습 ID가 맞지 않습니다")
            driver.execute_query("""CREATE CONSTRAINT research_lab_key IF NOT EXISTS
                FOR (n:ResearchLab) REQUIRE (n.lab_id, n.id) IS UNIQUE""", database_=args.database)
            with driver.session(database=args.database) as session:
                session.execute_write(seed_transaction, graph)
            records, _, _ = driver.execute_query("""MATCH (n:ResearchLab {lab_id: $lab})
                OPTIONAL MATCH (n)-[r]->(:ResearchLab {lab_id: $lab})
                RETURN count(DISTINCT n) AS nodes, count(r) AS relationships""",
                lab=LAB_ID, database_=args.database)
            print(json.dumps(records[0].data(), ensure_ascii=False))
        elif args.action == "queries":
            args.out.mkdir(parents=True, exist_ok=True)
            results = {}
            for name, query in QUERIES.items():
                records, _, keys = driver.execute_query(query, lab=LAB_ID, database_=args.database)
                results[name] = [record.data() for record in records]
                with (args.out / f"{name}.csv").open("w", encoding="utf-8-sig", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow(keys)
                    writer.writerows([[json.dumps(v, ensure_ascii=False) if isinstance(v, list) else v for v in record.values()] for record in records])
            (args.out / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
            print(json.dumps(results, ensure_ascii=False, indent=2))
            print(f"저장 위치: {args.out.resolve()}")
        else:
            driver.execute_query("MATCH (n:ResearchLab {lab_id: $lab}) DETACH DELETE n", lab=LAB_ID, database_=args.database)
            print("research-lab-v1 실습 노드만 삭제했습니다. 스키마 제약은 유지합니다.")


if __name__ == "__main__":
    main()
