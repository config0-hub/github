"""
# Copyright (C) 2025 Gary Leong <gary@config0.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from config0_publisher.terraform import TFConstructor


def _set_github_token(stack):
    """Set GitHub token from available input variables."""
    if stack.inputvars.get("github_token"):
        stack.set_variable("github_token",
                           stack.inputvars["github_token"],
                           tags="tf_exec_env",
                           types="str")
    elif stack.inputvars.get("GITHUB_TOKEN"):
        stack.set_variable("github_token",
                           stack.inputvars["GITHUB_TOKEN"],
                           tags="tf_exec_env",
                           types="str")
    elif stack.inputvars.get("github_token_hash"):
        stack.set_variable("github_token",
                           stack.b64_encode(stack.inputvars["github_token_hash"]),
                           tags="tf_exec_env",
                           types="str")

    if not stack.github_token:
        raise Exception("cannot retrieve github_token from inputargs")


def run(stackargs):

    # instantiate authoring stack
    stack = newStack(stackargs)

    # Add default variables
    stack.parse.add_required(key="name")
    
    stack.parse.add_required(key="url",
                             tags="tfvar",
                             types="str")

    stack.parse.add_required(key="repo")

    stack.parse.add_required(key="secret",
                             tags="tfvar",
                             types="str",
                             default="_random")

    stack.parse.add_optional(key="insecure_ssl",
                             tags="tfvar",
                             types="bool",
                             default='true')

    stack.parse.add_optional(key="active",
                             tags="tfvar",
                             types="bool",
                             default='true')

    stack.parse.add_optional(key="content_type",
                             tags="tfvar",
                             types="str",
                             default='json')

    stack.parse.add_optional(key="events",
                             tags="tfvar",
                             types="str",
                             default='push,pull_request')

    # Add execgroup
    stack.add_execgroup("config0-publish:::github::add_webhook",
                        "tf_execgroup")

    # Add substack
    stack.add_substack("config0-publish:::tf_executor")

    # Initialize Variables in stack
    stack.init_variables()
    stack.init_execgroups()
    stack.init_substacks()

    stack.set_variable("repository",
                       stack.repo,
                       tags="tfvar,db",
                       types="str")

    _set_github_token(stack)

    # use the terraform constructor (helper)
    tf = TFConstructor(stack=stack,
                       execgroup_name=stack.tf_execgroup.name,
                       provider="github",
                       resource_name=stack.name,
                       ssm_format=".env",
                       ssm_obj={"GITHUB_TOKEN": stack.github_token},
                       resource_type="repo_webhook")

    tf.include(maps={"webhook_url": "url"})

    tf.output(keys=["etag",
                    "events",
                    "url",
                    "repository"])

    # finalize the tf_executor
    stack.tf_executor.insert(display=True,
                             **tf.get())

    return stack.get_results()