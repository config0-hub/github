def run(stackargs):

    # instantiate authoring stack
    stack = newStack(stackargs)

    stack.parse.add_required(key="repo",
                             tags="upload_key",
                             types="str")

    stack.parse.add_required(key="stateful_id",
                             tags="upload_key",
                             types="str",
                             default="_random")

    # Add default variables
    stack.parse.add_optional(key="name",
                             default='null')

    stack.parse.add_optional(key="key_name",
                             tags="new_key,upload_key",
                             default='null')

    stack.parse.add_optional(key="schedule_id",
                             tags="new_key,upload_key",
                             types="str",
                             default="null")

    stack.parse.add_optional(key="run_id",
                             tags="new_key,upload_key",
                             types="str",
                             default="null")

    stack.parse.add_optional(key="job_instance_id",
                             tags="new_key,upload_key",
                             types="str",
                             default="null")

    stack.parse.add_optional(key="job_id",
                             tags="new_key,upload_key",
                             types="str",
                             default="null")

    # declare execution groups
    stack.add_substack("config0-hub:::new_ssh_key")
    stack.add_substack("config0-hub:::github_ssh_upload")

    # Initialize Variables in stack
    stack.init_variables()
    stack.init_substacks()

    if not stack.get_attr("key_name") and stack.get_attr("name"):
        stack.set_variable("key_name",
                           stack.key_name,
                           tags="new_key,upload_key",
                           types="str")

    if not stack.get_attr("key_name"):
        msg = "key_name or name variable has to be set"
        raise Exception(msg)

    # new ssh key
    arguments = stack.get_tagged_vars(tag="new_key",
                                      output="dict")

    human_description = "create ssh key name {}".format(stack.key_name)
    inputargs = {"arguments": arguments,
                 "automation_phase": "infrastructure",
                 "human_description": human_description}

    stack.new_ssh_key.insert(display=True, **inputargs)

    # upload ssh key
    arguments = stack.get_tagged_vars(tag="upload_key",
                                      output="dict")

    human_description =  "pubkey {} to {}".format(stack.key_name, stack.repo)
    inputargs = {"arguments": arguments,
                 "automation_phase": "infrastructure",
                 "human_description": human_description}

    stack.github_ssh_upload.insert(display=True, **inputargs)

    return stack.get_results()
