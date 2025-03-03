from os import path
from bot_variables import state
from bot_variables.config import InfoField, TemplateLinks, PullMarksGroupsFrom, EnrolmentSprdsht, MarksSprdsht
from wrappers import jsonc
from wrappers.pygs import FileName, AuthenticationError, WorksheetNotFound
from wrappers.pygs import update_cells_from_fields, get_google_client
from wrappers.pygs import get_spreadsheet, get_sheet_by_name, copy_spreadsheet
from wrappers.pygs import allow_access, share_with_anyone
from wrappers.utils import FormatText


def check_google_credentials():
    if not path.exists(FileName.SHEETS_CREDENTIALS):
        msg = f'Sheets credential file "{FileName.SHEETS_CREDENTIALS}" was not found.'
        msg += ' You will need to log on by clicking on this following link' 
        msg += ' and pasting the code from browser.'
        print(FormatText.warning(msg))
    try:
        get_google_client()
        print(FormatText.success("Google authorization was successful."))
    except Exception as error:
        msg = FormatText.error("Google authorization failed!"
                               " Did you forget to provide the credentials.json file?")
        raise AuthenticationError(msg) from error


def check_spreadsheet_from_id(spreadsheet_id):
    get_spreadsheet(spreadsheet_id)

# TODO: done? split into multiple function
def check_enrolment_sheet():
    # enrolment id may be empty
    if enrolment_id := state.info[InfoField.ENROLMENT_SHEET_ID]:
        enrolment_sheet = get_spreadsheet(enrolment_id)
    else:
        # enrolment id not found -> create a new sheet
        msg = f'Enrolment sheet ID is not specified {FileName.INFO_JSON} file.'
        msg += ' Creating a new spreadsheet...'
        print(FormatText.warning(msg))
        spreadsheet_name = EnrolmentSprdsht.TITLE.format(
                             course_code=state.info[InfoField.COURSE_CODE],
                             semester=state.info[InfoField.SEMESTER])
        enrolment_sheet = copy_spreadsheet(TemplateLinks.ENROLMENT_SHEET, 
                                           spreadsheet_name,
                                           state.info[InfoField.MARKS_FOLDER_ID])
    # finally update info file
    jsonc.update_info_field(InfoField.ENROLMENT_SHEET_ID, enrolment_sheet.id)
    # update routines and stuff (for both new and old enrolment sheet)
    update_cells_from_fields(enrolment_sheet, 
                             {EnrolmentSprdsht.CourseInfo.TITLE : 
                                 EnrolmentSprdsht.CourseInfo.CELL_TO_FILED_DICT})
    allow_access(enrolment_sheet.id, state.info[InfoField.ROUTINE_SHEET_ID])
    share_with_anyone(enrolment_sheet) # also gives it some time to fetch marks groups
    return enrolment_sheet
    
    
def check_marks_groups(enrolment_sheet):
    print(FormatText.wait(f'Fetching "{InfoField.MARKS_GROUPS}" from spreadsheet...'))
    routine_wrksht = get_sheet_by_name(enrolment_sheet, PullMarksGroupsFrom.WRKSHT)
    marks_groups = routine_wrksht.get_value(PullMarksGroupsFrom.CELL)
    marks_groups = jsonc.loads(marks_groups)
    print(FormatText.status(f'"{InfoField.MARKS_GROUPS}": {FormatText.bold(marks_groups)}'))
    # check sections in range 
    available_secs = set(range(1,1+state.info[InfoField.NUM_SECTIONS]))
    available_secs -= set(state.info[InfoField.MISSING_SECTIONS])
    if available_secs != {sec for group in marks_groups for sec in group}:
        msg = 'Marks groups contain sections that does not exist in'
        msg += f' {routine_wrksht.url}&range={PullMarksGroupsFrom.CELL}'
        raise ValueError(FormatText.error(msg))
    # update info json
    jsonc.update_info_field(InfoField.MARKS_GROUPS, marks_groups)
    

def check_marks_sheet(sec, group, marks_ids):
    if marks_ids.get(str(sec), ""): # key may not exist or value may be ""
        spreadsheet = get_spreadsheet(marks_ids[str(sec)])
    # no spreadsheet in info for the followings
    elif sec == group[0]: # sec is the first member of the group 
        print(FormatText.warning(f'Creating new spreadsheet for section {sec:02d}...'))
        spreadsheet = copy_spreadsheet(TemplateLinks.MARKS_SHEET,
                                       MarksSprdsht.TITLE.format(
                                           course_code=state.info[InfoField.COURSE_CODE],
                                           sections=','.join(f'{s:02d}' for s in group),
                                           semester=state.info[InfoField.SEMESTER]),
                                       state.info[InfoField.MARKS_FOLDER_ID])
        update_cells_from_fields(spreadsheet, 
                                 {MarksSprdsht.Meta.TITLE : 
                                     MarksSprdsht.Meta.CELL_TO_FILED_DICT})
    else: 
        # first group member has spreadsheet
        spreadsheet = get_spreadsheet(marks_ids[str(group[0])])
    marks_ids[str(sec)] = spreadsheet.id
    jsonc.update_info_field(InfoField.MARKS_SHEET_IDS, marks_ids)
    msg = f'Section {sec:02d} > Marks spreadsheet: "{spreadsheet.title}"'
    print(FormatText.success(msg))
    create_marks_sheet(spreadsheet, sec)
    # TODO: move all fixed strings to config.py
    
def check_marks_groups_and_sheets():
    check_marks_groups(state.info[InfoField.ENROLMENT_SHEET_ID])
    for marks_group in state.info[InfoField.MARKS_GROUPS]:
        for section in marks_group:
            check_marks_sheet(section, marks_group, 
                              state.info[InfoField.MARKS_SHEET_IDS].copy())
    

# create a worksheet for the section marks in spreadsheet
def create_marks_sheet(spreadsheet, sec):
    try: # success -> sec worksheet already exists
        sec_sheet = get_sheet_by_name(spreadsheet, MarksSprdsht.SecXX.TITLE.format(sec))
    except WorksheetNotFound: 
        # fail -> sec worksheet does not exist
        print(FormatText.status('Creating new worksheet...'))
        template_sheet = get_sheet_by_name(spreadsheet, MarksSprdsht.SecXX.TITLE.format(0))
        sec_sheet = template_sheet.copy_to(spreadsheet.id)
        sec_sheet.hidden = False
        sec_sheet.title = MarksSprdsht.SecXX.TITLE.format(sec)
        # TODO: populate with student ids and names
    # print(FormatText.status(f'Worksheet Name: {FormatText.BOLD}{sec_sheet.title}'))
    # print(FormatText.status(f'Worksheet Url: {FormatText.BOLD}{sec_sheet.url}')) 
    # TODO: move all fixed strings to config.py

    
# # TODO: check marks sheets
# def check_marks_sheets():
#     marks_groups = state.info[InfoField.MARKS_GROUPS]
#     marks_ids = state.info[InfoField.MARKS_SHEET_IDS].copy()
#     for group in marks_groups:
#         for sec in group:
#             if marks_ids.get(str(sec), ""): # key may not exist or value may be ""
#                 spreadsheet = get_spreadsheet(marks_ids[str(sec)])
#             # no spreadsheet in info for the followings
#             elif sec == group[0]: # sec is the first member of the group 
#                 print(FormatText.warning(f'Creating new spreadsheet for section {sec:02d}...')) 
#                 spreadsheet = copy_spreadsheet(TemplateLinks.MARKS_SHEET,
#                                                'Marks Spreadsheet for Sec ' + ','.join(f'{s:02d}' for s in group),
#                                                state.info[InfoField.MARKS_FOLDER_ID])
#                 update_cells_from_fields(spreadsheet, SheetCellToFieldDict.MARKS)
#             else: 
#                 # first group member has spreadsheet
#                 spreadsheet = get_spreadsheet(marks_ids[str(group[0])])
#             marks_ids[str(sec)] = spreadsheet.id
#             msg = f'Section {sec:02d} > Marks spreadsheet: "{spreadsheet.title}"'
#             print(FormatText.success(msg))
#             # now deal with worksheet
#             try: # success -> sec worksheet already exists
#                 sec_sheet = spreadsheet.worksheet_by_title(f"Sec {sec:02d}")
#             except pygs.WorksheetNotFound: 
#                 # fail -> sec worksheet does not exist
#                 print(FormatText.status('Creating new worksheet...'))
#                 template_sheet = spreadsheet.worksheet_by_title(f"Sec 00")
#                 print(FormatText.status(f'Template Worksheet Url: {FormatText.BOLD}{template_sheet.url}'))
#                 sec_sheet = template_sheet.copy_to(spreadsheet.id)
#                 sec_sheet.hidden = False
#                 sec_sheet.title = f'Sec {sec:02d}'
#             print(FormatText.status(f'Worksheet Name: {FormatText.BOLD}{sec_sheet.title}'))
#             print(FormatText.status(f'Worksheet Url: {FormatText.BOLD}{sec_sheet.url}'))   
#     # finally update json        
#     json.update_info_field(InfoField.MARKS_SHEET_IDS, marks_ids)
#     # TODO: populate with student ids and names
#     # TODO: move all fixed strings to config.py