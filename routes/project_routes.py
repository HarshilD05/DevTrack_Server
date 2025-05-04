# routes/project_routes.py
from flask import Blueprint
from controllers.project_controller import ProjectController

project_bp = Blueprint('project', __name__)

project_bp.route('', methods=['POST'])(ProjectController.create_project)
project_bp.route('', methods=['GET'])(ProjectController.get_user_projects)
project_bp.route('/<project_id>', methods=['GET'])(ProjectController.get_project)
project_bp.route('/<project_id>', methods=['PUT'])(ProjectController.update_project)
project_bp.route('/<project_id>/admin', methods=['POST'])(ProjectController.add_admin)
project_bp.route('/<project_id>/participant', methods=['POST'])(ProjectController.add_participant)
project_bp.route('/<project_id>/stages', methods=['PUT'])(ProjectController.update_stages)
project_bp.route('/<project_id>', methods=['DELETE'])(ProjectController.delete_project)