# CP-SAT-Test
Problem Statement:
A company has alot of employees and job posting. They want to find a way to automate posting recommendations for each person base on their field and previous assignment. Some posting need a specific type of field as well as citizenship. However, thye can up tier or down tier if needed.


Creating the dataset:
Positio (Pos): 
- ID
- Req Field
= Posting Domain and thier level
- Level of expertise that personnel need to under take this job
- Req Tier Level
- Req Citizenship

Personnel (Pers):
- ID
- Job Field
- Citizenship
- Staff Tier Level
- Pass test to be promoted a higher tier (If personnel is a beginner, they can only take beginner, But if they pass test_1, they can take a mid level job, same with a mid tier passing test_2 to take a senior tier)


Matching:
- Pos field = Pers Field or any
- Pos Tier = Pers Tier +-1 if they pass the test
- Pos hist tagging is a heavy consideration
- 
