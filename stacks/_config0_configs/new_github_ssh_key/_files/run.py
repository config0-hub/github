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

def run(stackargs):

    # instantiate authoring stack
    stack = newStack(stackargs)

    # Required parameters
    stack.parse.add_required(key="repo",
                             tags="upload_key",
                             types="str")

    stack.parse.add_required(key="stateful_id",
                             tags="upload_key",
                             types="str",
                             default="_random")

    # Optional parameters
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

    stack.parse.add_optional(key="github_token",
                             tags="upload_key",
                             types="str",
                             default="null")

    # Declare execution groups
    stack.add_substack("config0-publish:::new_ssh_key")
    stack.add_substack("config0-publish:::github_ssh_upload")

    # Initialize Variables in stack
    stack.init_variables()
    stack.init_substacks()

    # Set key_name if not provided but name is available
    if not stack.get_attr("key_name") and stack.get_attr("name"):
        stack.set_variable("key_name",
                           stack.key_name,
                           tags="new_key,upload_key",
                           types="str")

    if not stack.get_attr("key_name"):
        msg = "key_name or name variable has to be set"
        raise Exception(msg)

    # Create new SSH key
    arguments = stack.get_tagged_vars(tag="new_key",
                                      output="dict")

    human_description = f"create ssh key name {stack.key_name}"
    inputargs = {"arguments": arguments,
                 "automation_phase": "infrastructure",
                 "human_description": human_description}

    stack.new_ssh_key.insert(display=True, **inputargs)

    # Upload SSH key to GitHub
    arguments = stack.get_tagged_vars(tag="upload_key",
                                      output="dict")

    human_description = f"pubkey {stack.key_name} to {stack.repo}"
    inputargs = {"arguments": arguments,
                 "automation_phase": "infrastructure",
                 "human_description": human_description}

    stack.github_ssh_upload.insert(display=True, **inputargs)

    return stack.get_results()