import hikari, crescent
from bot_variables import state
from bot_variables.config import ClassType
from wrappers.utils import FormatText
from wrappers.discord import get_sec_role_name, get_sec_role, get_sec_category_name, get_sec_category

plugin = crescent.Plugin[hikari.GatewayBot, None]()

# check if all sections' roles and channels are in server
async def check_discord_sec():
    # iterate over available theory & lab sections
    for class_type in ClassType.BOTH:
        for sec in state.available_sections:
            role = get_sec_role(sec, class_type)
            state.sec_roles[sec][class_type] = role
            if sec == 1: # skip on section 01 (template)
                continue
            if not role:
                role = await create_sec_role(sec, class_type)
            category: hikari.GuildCategory = get_sec_category(sec, class_type)
            if not category:
                category = await create_sec_category(sec, class_type, role)
        # reorder sec 01 lab after all theories
        if class_type == ClassType.THEORY:
            last_theory_category = category
        await get_sec_category(1,ClassType.LAB).edit(position=last_theory_category.position+1)


async def create_sec_role(section: int, class_type: ClassType):
    template_role = get_sec_role(1, class_type)
    role_name = get_sec_role_name(section, class_type)
    new_role = await create_role_from_template(role_name, template_role)
    return new_role

# clone role with new name
async def create_role_from_template(role_name: str, template_role: hikari.Role):
    msg = FormatText.bold('@'+role_name)
    print(FormatText.warning(f"Creating {msg} role..."))
    new_role = await plugin.app.rest.create_role(
        state.guild, 
        name=role_name, 
        permissions=template_role.permissions, 
        color=template_role.color)
    print(FormatText.success(f"Created {msg} role successfully."))
    return new_role


def load_sec_template(class_type: ClassType):
    # skip if templated fetched earlier
    if state.sec_template[class_type]:
        return
    # fetch template
    template_role = get_sec_role(1, class_type)
    template_category = get_sec_category(1, class_type)
    # update state variable
    state.sec_template[class_type] = {
        'role': template_role,
        'category': template_category,
        'channels': [
            channel for _, channel in state.guild.get_channels().items()
                if channel.parent_id == template_category.id
        ]
    }

async def create_sec_category(section: int, class_type: ClassType, new_role: hikari.Role):
    # fetch template from section 01
    load_sec_template(class_type)
    # clone category with permissions
    category_name = get_sec_category_name(section, class_type)
    new_category = await create_channel_from_template(category_name, 
                                                      new_role, 
                                                      state.sec_template[class_type]['category'], 
                                                      state.sec_template[class_type]['role'])
    # clone channels under template category
    for template_channel in state.sec_template[class_type]['channels']:
        await create_channel_from_template(template_channel.name, 
                                           new_role,
                                           template_channel, 
                                           state.sec_template[class_type]['role'], 
                                           new_category)
    return new_category

# clone category with new name
async def create_channel_from_template(new_channel_name: str, new_role: hikari.Role,
                                       template_channel: hikari.PermissibleGuildChannel,
                                       template_role: hikari.Role,
                                       parent_category: hikari.GuildCategory = None):
    msg = FormatText.bold('#'+new_channel_name)
    if template_channel.type == hikari.ChannelType.GUILD_CATEGORY:
        msg += " category"
        print(FormatText.warning(f"Creating {msg}..."))
    else:
        msg += " channel"
        print(FormatText.status(f"Creating {msg}..."))
    # create channel in server
    create_channel_dict = {
        hikari.ChannelType.GUILD_CATEGORY: state.guild.create_category,
        hikari.ChannelType.GUILD_VOICE: state.guild.create_voice_channel,
        hikari.ChannelType.GUILD_TEXT: state.guild.create_text_channel,
    }
    create_channel = create_channel_dict[template_channel.type]
    new_channel : hikari.PermissibleGuildChannel = await create_channel(
                name=new_channel_name, 
                permission_overwrites=template_channel.permission_overwrites.values())
    await new_channel.edit(parent_category=parent_category)
    # copy permission overwrite from template to new role
    permission_overwrite = new_channel.permission_overwrites[template_role.id]
    await new_channel.remove_overwrite(template_role.id)
    await new_channel.edit_overwrite(new_role, 
                                     allow=permission_overwrite.allow,
                                     deny=permission_overwrite.deny)
    if template_channel.type == hikari.ChannelType.GUILD_CATEGORY:
        print(FormatText.success(f"Created {msg} successfully."))
    return new_channel