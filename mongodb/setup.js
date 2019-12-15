DBNAMES = ['cache_db', 'reseller_db'];

db.auth('admin', 'admin');

for (let dbname in DBNAMES) {
  db = db.getSiblingDB(dbname);
  db.createUser({
    user: 'webapp',
    pwd: 'webapp',
    roles: [
      {
        role: 'dbOwner',
        db: dbname
      }
    ]
  });
}
