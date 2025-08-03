from mako.template import Template
from ptsched.structures import ScheduleTransformed


def render_default(schedule: ScheduleTransformed):
    result = []
    template = Template("""% for _class in day.classes:
${_class.name + ":"}
        % for task in _class.tasks:
${task.name}
        % endfor
        % if not loop.last:

        % endif
    % endfor""")
    for day in schedule.days:
        result.append({"date": day.date, "content": template.render(day=day)})

    return result


def render_markdown(schedule: ScheduleTransformed):
    result = []
    template = Template("""# Tasks: ${day.date}

    % for _class in day.classes:
${"##"} ${_class.name}
        % if _class.tasks:

        % endif
        % for task in _class.tasks:
- [ ] ${task.name}
        % endfor
        % if not loop.last:

        % endif
    % endfor""")
    for day in schedule.days:
        result.append({"date": day.date, "content": template.render(day=day)})

    return result
