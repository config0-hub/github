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


def run(stackargs):

    # instantiate authoring stack
    stack = newStack(stackargs)

    # Required parameters
    stack.parse.add_required(key="repo",
                             tags="upload_key",
                             types="str")

    # Optional parameters
    stack.parse.add_optional(key="name",
                             default='null')

    stack.parse.add_optional(key="key_name",
                             tags="tfvar,db,upload_key",
                             default='null')

    # The key pair's region. AWS keeps the private half in SSM there.
    stack.parse.add_optional(key="aws_default_region",
                             default="ap-northeast-1",
                             tags="tfvar,db,resource,tf_exec_env",
                             types="str")

    stack.parse.add_optional(key="github_token",
                             tags="upload_key",
                             types="str",
                             default="null")

    # Declare execution groups
    stack.add_execgroup("config0-hub:::aws::ssh_key_pair",
                        "tf_execgroup")
    stack.add_substack("config0-hub:::config0_core::tf_executor")
    stack.add_substack("config0-hub:::github::github_ssh_upload")

    # Initialize Variables in stack
    stack.init_variables()
    stack.init_execgroups()
    stack.init_substacks()

    # Set key_name if not provided but name is available
    if not stack.get_attr("key_name") and stack.get_attr("name"):
        stack.set_variable("key_name",
                           stack.name,
                           tags="tfvar,db,upload_key",
                           types="str")

    if not stack.get_attr("key_name"):
        msg = "key_name or name variable has to be set"
        raise Exception(msg)

    # Create the key pair. EC2 generates it and keeps the private half in
    # SSM; the ssh_key_pair row names that parameter, never the key.
    tf = TFConstructor(stack=stack,
                       provider="aws",
                       execgroup_name=stack.tf_execgroup.name,
                       tf_runtime="tofu:1.11.14",
                       resource_name=stack.key_name,
                       resource_type="ssh_key_pair")

    tf.include(keys=["key_name",
                     "key_pair_id",
                     "public_key",
                     "private_key_ssm_path"])

    stack.tf_executor.insert(display=True, **tf.get())

    # Upload the public half to GitHub. github_ssh_upload reads it from the
    # ssh_key_pair row and derives its own stateful_id.
    arguments = stack.get_tagged_vars(tag="upload_key",
                                      output="dict")

    human_description = f"pubkey {stack.key_name} to {stack.repo}"
    inputargs = {"arguments": arguments,
                 "automation_phase": "infrastructure",
                 "human_description": human_description}

    stack.github_ssh_upload.insert(display=True, **inputargs)

    return stack.get_results()
