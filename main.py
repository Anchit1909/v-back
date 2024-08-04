from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List, Dict
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
def read_root():
    return {'Ping': 'Pong'}

class Node(BaseModel):
    id: str
    type: str
    data: Dict

class Edge(BaseModel):
    id: str
    source: str
    target: str

class Pipeline(BaseModel):
    nodes: List[Node]
    edges: List[Edge]

@app.post('/pipelines/parse')
async def parse_pipeline(pipeline: Pipeline):
    num_nodes = len(pipeline.nodes)
    num_edges = len(pipeline.edges)
    
    graph = {node.id: [] for node in pipeline.nodes}
    in_degree = {node.id: 0 for node in pipeline.nodes}
    
    for edge in pipeline.edges:
        graph[edge.source].append(edge.target)
        in_degree[edge.target] += 1
    
    zero_in_degree_queue = [node_id for node_id in in_degree if in_degree[node_id] == 0]
    topo_sorted = []

    while zero_in_degree_queue:
        current = zero_in_degree_queue.pop(0)
        topo_sorted.append(current)

        for neighbor in graph[current]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                zero_in_degree_queue.append(neighbor)

    is_dag = len(topo_sorted) == num_nodes
    
    return {"num_nodes": num_nodes, "num_edges": num_edges, "is_dag": is_dag}
