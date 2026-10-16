import tempfile, unittest
from pathlib import Path
import app as bvm

class AppTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        bvm.DB_PATH=Path(self.tmp.name)/"test.sqlite3"
        bvm.app.config.update(TESTING=True, SECRET_KEY="test")
        bvm.init_db()
        self.client=bvm.app.test_client()
    def tearDown(self): self.tmp.cleanup()
    def test_home(self):
        self.assertEqual(self.client.get("/").status_code,200)
    def test_bad_login_redirects(self):
        r=self.client.post("/authenticate",data={"voter_id":"UNKNOWN","pin":"0000"})
        self.assertEqual(r.status_code,302)
    def test_dashboard(self):
        self.assertEqual(self.client.get("/dashboard").status_code,200)

if __name__=="__main__": unittest.main()
