Input: SQL code as list of strings
e.g. ['SELECT * FROM ', '/* select my data */', 'MYSCHEMA.MYTABLE;']
Output: 2D list of strings, replicating input and providing tags indicating type of input
e.g. [['SELECT * FROM', 'other'], ['/* select my data */', 'multilinecomment'], ['MYSCHEMA.MYTABLE;', 'other']]
