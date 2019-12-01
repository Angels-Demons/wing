import datetime


def log(subject, message, user=None):
    f = open("log.txt", "a")
    f.write(subject + "\t: ")
    f.write(datetime.datetime.now().__str__() + ": ")
    if user:
        f.write(str(user.phone) + " (%s): " % user.profile.app_version + "\t")
    f.write(message)
    f.write("\n")
    f.close()


def error(message, user):
    log("ERROR", message, user)


def info(message, user):
    log("INFO", message, user)


def warning(message, user):
    log("WARNING", message, user)


def debug(message, user):
    log("DEBUG", message, user)
