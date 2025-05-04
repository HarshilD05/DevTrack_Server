# routes/task_routes.py
from flask import Blueprint
from controllers.task_controller import TaskController

task_bp = Blueprint('task', __name__)

task_bp.route('/project/<project_id>', methods=['POST'])(TaskController.create_task)
task_bp.route('/project/<project_id>', methods=['GET'])(TaskController.get_project_tasks)
task_bp.route('/user', methods=['GET'])(TaskController.get_user_tasks)
task_bp.route('/<task_id>', methods=['GET'])(TaskController.get_task)
task_bp.route('/<task_id>', methods=['PUT'])(TaskController.update_task)
task_bp.route('/<task_id>/request-status', methods=['POST'])(TaskController.request_status_update)
task_bp.route('/approve-status/<request_id>', methods=['POST'])(TaskController.approve_status_change)
task_bp.route('/<task_id>', methods=['DELETE'])(TaskController.delete_task)