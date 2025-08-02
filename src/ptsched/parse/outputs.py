from mako.template import Template


def render_default(schedule):
    result = []
    template = Template("""% for _class in day["classes"]:
${_class["name"] + ":"}
        % for task in _class["tasks"]:
${task}
        % endfor
        % if not loop.last:

        % endif
    % endfor""")
    for day in schedule["days"]:
        result.append({"date": day["date"], "content": template.render(day=day)})

    return result


def render_markdown(schedule):
    result = []
    template = Template("""# Tasks: ${day["date"]}

    % for _class in day["classes"]:
${"##"} ${_class["name"]}
        % if _class["tasks"]:

        % endif
        % for task in _class["tasks"]:
- [ ] ${task}
        % endfor
        % if not loop.last:

        % endif
    % endfor""")
    for day in schedule["days"]:
        result.append({"date": day["date"], "content": template.render(day=day)})

    return result
