# -*- coding: utf-8 -*-
from . import sign_template # assuming this file exists and contains sign_template extensions
from . import project_task   # This file now contains all project/task extensions AND the new contract models
from . import engineering_task_commitment # These are your *existing* commitment models
from . import engineering_project_commitment # These are your *existing* commitment models
from . import res_company # These are your *existing* commitment models
# REMOVE: from . import engineering_project_contract (as it doesn't exist as a separate file and isn't needed)