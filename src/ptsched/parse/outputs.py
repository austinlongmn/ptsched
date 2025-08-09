from mako.template import Template
from ptsched.structures import ScheduleTransformed


def render_default(schedule: ScheduleTransformed):
    template = Template("""%for day in schedule.days:
${day.date}:

            % for _class in day.classes:
${_class.name + ":"}
            % for task in _class.tasks:
${task.name}
            % endfor
            % if not loop.last:

            % endif
        % endfor
        % if not loop.last:

        % endif
    % endfor""")

    return template.render(schedule=schedule)


def render_markdown(schedule: ScheduleTransformed):
    template = Template("""%for day in schedule.days:
# Tasks: ${day.date}

        % for _class in day.classes:
${"##"} ${_class.name}
            % if _class.tasks:

            % endif
            % for task in _class.tasks:
- [ ] ${task.name}
            % endfor
            % if not loop.last:

            % endif
        % endfor
        % if not loop.last:

        % endif
    % endfor""")

    return template.render(schedule=schedule)
