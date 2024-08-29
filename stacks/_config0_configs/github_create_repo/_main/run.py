from config0_publisher.terraform import TFConstructor

def _set_github_token(stack):

    # insert the github token in the "tf_exec_env"
    # environment, use the var tag "tf_exec_env"
    if stack.github_token:
        stack.logger.debug('github_token explicity set through stack argument')
        return

    if stack.inputvars.get("GITHUB_TOKEN"):
        stack.set_variable("github_token",
                           stack.inputvars["GITHUB_TOKEN"],
                           tags="tf_exec_env",
                           types="str")

    elif stack.inputvars.get("github_token"):
        stack.set_variable("github_token",
                           stack.inputvars["github_token"],
                           tags="tf_exec_env",
                           types="str")
    elif stack.inputvars.get("github_token_hash"):
        stack.set_variable("github_token",
                           stack.b64_decode(stack.inputvars["github_token_hash"]),
                           tags="tf_exec_env",
                           types="str")
    elif stack.inputvars.get("GITHUB_TOKEN_HASH"):
        stack.set_variable("github_token",
                           stack.b64_decode(stack.inputvars["GITHUB_TOKEN_HASH"]),
                           tags="tf_exec_env",
                           types="str")

    if not stack.github_token:
        raise Exception("cannot retrieve github_token from inputargs")

def run(stackargs):

    # instantiate authoring stack
    stack = newStack(stackargs)

    # Add default variables
    stack.parse.add_required(key="repository",
                             tags="tfvar,db",
                             types="str",
                             default=None)

    stack.parse.add_optional(key="visibility",
                             tags="tfvar",
                             types="str",
                             default="private")

    stack.parse.add_optional(key="has_issues",
                             tags="tfvar,db",
                             types="boolean",
                             default="true")

    stack.parse.add_optional(key="has_projects",
                             tags="tfvar,db",
                             types="boolean",
                             default="false")

    stack.parse.add_optional(key="has_wiki",
                             tags="tfvar,db",
                             types="boolean",
                             default="false")

    stack.parse.add_optional(key="delete_branch_on_merge",
                             tags="tfvar,db",
                             types="boolean",
                             default="true")

    stack.parse.add_optional(key="default_branch",
                             tags="tfvar",
                             types="str",
                             default="main")

    stack.parse.add_optional(key="github_token",
                             tags="tf_exec_env",
                             types="str",
                             default="null")

    # Add execgroup
    stack.add_execgroup("config0-publish:::github::create_repo",
                        "tf_execgroup")

    # Add substack
    stack.add_substack("config0-publish:::tf_executor")

    # Initialize Variables in stack
    stack.init_variables()
    stack.init_execgroups()
    stack.init_substacks()

    _set_github_token(stack)

    # use the terraform constructor (helper)
    # but this is optional
    tf = TFConstructor(stack=stack,
                       execgroup_name=stack.tf_execgroup.name,
                       provider="github",
                       resource_name=stack.repository,
                       ssm_format=".env",
                       ssm_obj={"GITHUB_TOKEN": stack.github_token},
                       resource_type="repository",
                       terraform_type="github_repository")

    tf.include(keys=["default_branch",
                     "git_clone_url",
                     "http_clone_url",
                     "name",
                     "ssh_clone_url",
                     "visibility"])

    # publish the info
    if _publish:
        tf.output(keys=["git_clone_url",
                        "http_clone_url",
                        "ssh_clone_url"])

    # finalize the tf_executor
    stack.tf_executor.insert(display=True,
                             **tf.get())

    return stack.get_results()
