from config0_publisher.terraform import TFConstructor


def _get_ssh_public_key(stack):

    _lookup = {"must_be_one": True,
               "resource_type": "ssh_key_pair",
               "provider": "config0",
               "name": stack.key_name}

    results = stack.get_resource(decrypt=True, 
                                 **_lookup)[0]

    return stack.b64_encode(results["public_key"])

def run(stackargs):

    # instantiate authoring stack
    stack = newStack(stackargs)

    # Add default variables
    stack.parse.add_required(key="repo")

    stack.parse.add_optional(key="key_name",
                             tags="tfvar,db",
                             types="str",
                             default=None)

    stack.parse.add_optional(key="name",
                             default=None)

    stack.parse.add_optional(key="public_key_hash",
                             tags="tfvar",
                             types="str",
                             default=None)

    stack.parse.add_optional(key="public_key",
                             types="str",
                             default=None)

    stack.parse.add_optional(key="read_only",
                             tags="tfvar,db",
                             types="bool",
                             default="true")

    stack.parse.add_optional(key="github_token",
                             tags="runtime_settings",
                             types="str",
                             default="null")

    # Add execgroup
    stack.add_execgroup("config0-hub:::github::ssh_key_upload",
                        "tf_execgroup")

    # Add substack
    stack.add_substack("config0-hub:::tf_executor")

    # Initialize Variables in stack
    stack.init_variables()
    stack.init_execgroups()
    stack.init_substacks()

    if not stack.get_attr("key_name") and stack.get_attr("name"):
        stack.set_variable("key_name",
                           stack.name,
                           tags="tfvar,db",
                           types="str")

    stack.set_variable("repository",
                       stack.repo,
                       tags="tfvar,db",
                       types="str")

    if not stack.get_attr("key_name"):
        msg = "key_name or name variable has to be set"
        raise Exception(msg)

    _publish = None

    # publish key expected to be encoded as base64
    if not stack.get_attr("public_key_hash"):

        if not stack.get_attr("public_key") and stack.inputvars.get("public_key"):

            stack.logger.debug_highlight("public key found in inputvars")

            stack.set_variable("public_key_hash",
                               stack.inputvars["public_key"],
                               tags="tfvar",
                               types="str")

            _publish = None

        elif not stack.get_attr("public_key"):

            _public_key_hash = _get_ssh_public_key(stack)

            if _public_key_hash:
                stack.logger.debug_highlight("public key found in resources table")

            stack.set_variable("public_key_hash",
                               _public_key_hash,
                               tags="tfvar",
                               types="str")

            _publish = True

    if not stack.get_attr("public_key_hash"):
        msg = "public_key/public_key_hash is missing"
        raise Exception(msg)

    # insert the github token in the "runtime_settings"
    # environment, use the var tag "runtime_settings"
    if stack.inputvars.get("GITHUB_TOKEN"):
        stack.set_variable("github_token",
                           stack.inputvars["GITHUB_TOKEN"],
                           tags="runtime_settings",
                           types="str")

    elif stack.inputvars.get("github_token"):
        stack.set_variable("github_token",
                           stack.inputvars["github_token"],
                           tags="runtime_settings",
                           types="str")

    if not stack.github_token:
        raise Exception("cannot retrieve github_token from inputargs")

    ssm_obj = { "GITHUB_TOKEN": stack.github_token }

    # use the terraform constructor (helper)
    # but this is optional
    tf = TFConstructor(stack=stack,
                       execgroup_name=stack.tf_execgroup.name,
                       provider="github",
                       resource_name=stack.key_name,
                       ssm_format=".env",
                       ssm_obj=ssm_obj,
                       resource_type="repo_deploy_key",
                       terraform_type="github_repository_deploy_key")

    tf.include(keys=["id",
                     "etag",
                     "repository",
                     "read_only"])

    tf.include(maps={"key_name": "title"})

    # publish the info
    if _publish:
        tf.output(keys=["id",
                        "etag",
                        "repository",
                        "key_name",
                        "resource_type"])

    # finalize the tf_executor
    stack.tf_executor.insert(display=True,
                             **tf.get())

    return stack.get_results()
