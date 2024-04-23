from os.path import dirname, basename, isfile, join
from sqlalchemy.pool import QueuePool
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(engine_options={"pool_size": 10, 'pool_recycle': 280, "poolclass":QueuePool, "pool_pre_ping":True})

import glob
modules = glob.glob(join(dirname(__file__), "*.py"))
__all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]

#__all__ = [ "bac", "level", "level_value", "level_value_relation", "exoneration", "school", "domain", "subdomain", "major", "subject", "foreign_language", "course", 
#            "course_foreign_language_relation", "course_level_relation", "course_subject_relation"]
