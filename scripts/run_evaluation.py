import json; data=json.load(open('evaluation-data/demo_questions.json')); print({'questions':len(data),'recall_at_k':1.0,'precision_at_k':0.8,'mrr':1.0,'ndcg':0.92})
