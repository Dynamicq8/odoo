from odoo import models, fields, api

class SignTemplatePatch(models.Model):
    _inherit = 'sign.template'

    def action_rename_template_fields(self):
        """
        Action to rename fields on the current sign template.
        This is for when UI is not cooperating.
        """
        self.ensure_one() # Ensures this runs on a single template at a time

        # --- IMPORTANT: Configure your field renames here ---
        # Map CURRENT_NAME_ON_TEMPLATE : DESIRED_NAME_FOR_AUTOFILL
        replacements_map = {
            'Text': 'Governorate',    # Assuming you have a 'Text' field for Governorate
            'Date': 'Date',           # Assuming you have a 'Date' field with name 'Date'
            'Text 1': 'Region',
            'Text 2': 'Block',
            'Text 3': 'Plot',
            'Text 4': 'Street',
            'Name 1': 'Name',         # Assuming you have a 'Name' field (maybe default is 'Name 1')
            # Add all other mappings as needed based on your template's actual field names
        }

        updated_fields_count = 0
        for item in self.sign_item_ids: # Iterate through fields (sign.item) on this template
            if item.name in replacements_map:
                new_name = replacements_map[item.name]
                if item.name != new_name:
                    item.write({'name': new_name})
                    updated_fields_count += 1
                    self.env.user.notify_info(f"Renamed field '{item.name}' to '{new_name}'")
                else:
                    self.env.user.notify_warning(f"Field '{item.name}' already has the desired name.")
            else:
                self.env.user.notify_warning(f"Field '{item.name}' not in replacement map. No change.")

        self.env.user.notify_info(f"Field renaming complete. {updated_fields_count} fields updated.")
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': "Fields Renamed",
                'message': f"{updated_fields_count} fields were renamed successfully.",
                'sticky': False,
                'type': 'success',
            }
        }
