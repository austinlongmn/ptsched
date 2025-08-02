import sys


def output_default(result, outfile):
    try:
        counter = 0
        sorted_days = sorted(result.keys())
        length = len(sorted_days)
        for day in sorted_days:
            print(day + ":\n", file=outfile)

            sorted_courses = sorted(result[day].keys())
            counter2 = 0
            length2 = len(sorted_courses)
            for course in sorted_courses:
                print(course + ":", file=outfile)
                for task in result[day][course]:
                    print(task, file=outfile)
                if not (counter >= length - 1 and counter2 >= length2 - 1):
                    print(file=outfile)
                counter2 += 1
            counter += 1
    finally:
        if outfile != sys.stdout:
            outfile.close()


def output_markdown(result, outfile):
    try:
        counter = 0
        sorted_days = sorted(result.keys())
        length = len(sorted_days)
        for day in sorted_days:
            print("# Tasks: " + day + "\n", file=outfile)

            sorted_courses = sorted(result[day].keys())
            counter2 = 0
            length2 = len(sorted_courses)
            for course in sorted_courses:
                print("## " + course + "\n", file=outfile)
                for task in result[day][course]:
                    print("- [ ] " + task, file=outfile)
                if not (counter >= length - 1 and counter2 >= length2 - 1):
                    print(file=outfile)
                counter2 += 1
            counter += 1
    finally:
        if outfile != sys.stdout:
            outfile.close()
