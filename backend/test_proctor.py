from proctor import check_violation


user_id = "student_1"

# First cheating attempt
objects_1 = ["person", "cell phone"]
status, count = check_violation(objects_1, user_id)
print("Attempt 1:", status, "Warnings:", count)

# Second cheating attempt
objects_2 = ["person", "book"]
status, count = check_violation(objects_2, user_id)
print("Attempt 2:", status, "Warnings:", count)
