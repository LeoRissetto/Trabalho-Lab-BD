import psycopg2

con = psycopg2.connect(
    host='localhost',
    database='postgres',
    user='postgres',
    password='mysecretpassword',
    port=5432
)
cur = con.cursor()
cur.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")

for (tabela,) in cur.fetchall():
    cur.execute(f"DROP TABLE IF EXISTS {tabela} CASCADE")
con.commit()
print("Banco limpo com sucesso!")

with open("/home/leorissetto/Developer/Trabalho-Lab-BD/Código/SQL/tabelas_postgresql.sql") as f:
    sql_script = f.read()
for statement in sql_script.split(';'):
    stmt = statement.strip()
    if stmt:
        cur.execute(stmt)
con.commit()
print("Script SQL executado com sucesso!")
cur.close()
con.close()