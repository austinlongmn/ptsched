from mako.template import Template
from ptsched.structures import ScheduleReverse


def generate_file(schedule: ScheduleReverse):
    template = Template("""${schedule.metadata.start_date.strftime('%-d %b %Y')} - ${schedule.metadata.end_date.strftime('%-d %b %Y')}

% for class_ in schedule.classes:
# ${class_.name}

    % for day in class_.days:
- ${day.date.strftime('%a %-d')}

        % for task in day.tasks:
${task.name}
        % endfor
    % endfor
% endfor""")

    return template.render(schedule=schedule)
