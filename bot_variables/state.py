import hikari, collections
import miru as _miru
import pandas as pd
from bot_variables.config import ClassType
miru_client:  _miru.Client= None
# debug?
is_debug = False
# everything passed to info json file
info : dict = {}
# guild related objects
guild : hikari.Guild = None
eee_guild : hikari.Guild = None

available_sections : list = []

sec_template = {ClassType.THEORY: {}, ClassType.LAB: {}}
sec_roles = collections.defaultdict(dict[str, hikari.Role]) # dict of dict
all_sec_roles : set = {}

faculty_role : hikari.Role = None
faculty_sub_roles : dict = {}
st_role : hikari.Role = None
admin_role : hikari.Role = None
bot_admin_role : hikari.Role = None
student_role : hikari.Role = None

df_student : pd.DataFrame = None
df_routine : pd.DataFrame = None
df_marks_section : pd.DataFrame = None