from transformers import AutoTokenizer, AutoModel
import torch
from tqdm.auto import tqdm
import sys

sys.path.append('C:/Users/tjker/Desktop/Research/Projects/lit_review/lit_review')
import utils 
  
def compute_embedding(text, tokenizer, model):
        inputs = tokenizer(text, return_tensors="pt")
        with torch.no_grad():     
            outputs = model(**inputs) 
        return outputs.last_hidden_state.mean(dim=1).squeeze(0).tolist()

def main(config_file="C:/Users/tjker/Desktop/Research/Projects/lit_review/configs/abstract_embeddings.yaml"):
    config = utils.load_config(config_file)
    kg = utils.load_kg(config)

    tokenizer = AutoTokenizer.from_pretrained(config['model']['model_id'])
    model = AutoModel.from_pretrained(config['model']['model_id'])

    result = kg.query("""
        MATCH (p:Paper) 
        RETURN elementId(p) AS node_id, p.abstract AS abstract
        """
    )
    
    for record in tqdm(result):       
        if record["abstract"]:
            embedding = compute_embedding(record["abstract"], tokenizer, model)
            kg.query("""
                MATCH (p:Paper) WHERE elementId(p) = $node_id
                SET p.abstractEmbedding = $embedding
                RETURN elementId(p) AS node_id, p.abstract AS abstract
                """, params={"node_id":record["node_id"], "embedding":embedding}
            )
            
    kg.query("""
        CREATE VECTOR INDEX abstract_embeddings IF NOT EXISTS
        FOR (p:Paper) ON (p.abstractEmbedding) 
        OPTIONS { indexConfig: {
            `vector.dimensions`: $dimension,
            `vector.similarity_function`: $similarity
        }}""", params={'dimension': config['embedding']['size'], 'similarity': config['embedding']['similarity']}
    )
    
    kg.query("""
        CREATE FULLTEXT INDEX paperTitleIndex FOR (p:Paper) ON EACH [p.title]
        """
    )

if __name__ == "__main__":
    main()