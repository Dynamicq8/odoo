# -*- coding: utf-8 -*-
from odoo import models, fields, api, _, http
from odoo.exceptions import UserError, ValidationError
import datetime
import urllib.parse

# ==============================================================================
#  WORKFLOW TEMPLATES (خرائط سير العمل)
# ==============================================================================
WORKFLOW_TEMPLATES = {
    # 1. سكن خاص + بناء جديد
    'res_new':[
        {'code': 'rn_1_1', 'name': '1- تصميم الكروكي', 'stage': 'المرحلة الأولى', 'role': 'architect_id', 'depends_on': []},
        {'code': 'rn_1_2', 'name': '2- تجميع المستندات', 'stage': 'المرحلة الأولى', 'role': 'secretary_id', 'depends_on':[]},
        {'code': 'rn_1_3', 'name': '3- العقد وتحصيل الدفعة الأولى', 'stage': 'المرحلة الأولى', 'role': 'accountant_id', 'depends_on':[]},
        {'code': 'rn_1_4', 'name': '4- تجهيز النماذج والتعهدات والتوقيع', 'stage': 'المرحلة الأولى', 'role': 'secretary_id', 'depends_on':[]},
        {'code': 'rn_1_5', 'name': '5- فحص التربة - كتاب الكهرباء', 'stage': 'المرحلة الأولى', 'role': 'secretary_id', 'depends_on':[]},

        {'code': 'rn_2_1', 'name': '1- سيستم الأعمدة', 'stage': 'المرحلة الثانية', 'role': 'structural_id', 'depends_on': ['rn_1_1']},
        {'code': 'rn_2_2', 'name': '2- الواجهات', 'stage': 'المرحلة الثانية', 'role': 'facade_draftsman_id', 'depends_on':['rn_1_1']},
        {'code': 'rn_2_3', 'name': '3- رسم مخطط البلدية', 'stage': 'المرحلة الثانية', 'role': 'muni_draftsman_id', 'depends_on': ['rn_2_1']},

        {'code': 'rn_3_1', 'name': '1- إرسال للبلدية', 'stage': 'المرحلة الثالثة', 'role': 'secretary_id', 'depends_on': ['rn_2_3']},
        {'code': 'rn_3_2', 'name': '2- اعتماد البلدية', 'stage': 'المرحلة الثالثة', 'role': 'secretary_id', 'depends_on':['rn_3_1']},
        {'code': 'rn_3_3', 'name': '3- تحصيل الدفعة الأخيرة من العقد', 'stage': 'المرحلة الثالثة', 'role': 'accountant_id', 'depends_on': ['rn_3_2']},

        {'code': 'rn_4_1', 'name': '1- تصميم المخطط الإنشائي', 'stage': 'المرحلة الرابعة', 'role': 'structural_id', 'depends_on': ['rn_3_2']},
        {'code': 'rn_4_2', 'name': '2- تصميم مخطط الصحي', 'stage': 'المرحلة الرابعة', 'role': 'draftsman_id', 'depends_on':['rn_3_2']},
        {'code': 'rn_4_3', 'name': '3- تصميم مخطط الكهرباء', 'stage': 'المرحلة الرابعة', 'role': 'electrical_id', 'depends_on': ['rn_3_2']},
        {'code': 'rn_4_4', 'name': '4- تصميم مخطط الفرش', 'stage': 'المرحلة الرابعة', 'role': 'architect_id', 'depends_on': ['rn_3_2']},
        {'code': 'rn_4_5', 'name': '5- تجهيز الكراسة النهائية', 'stage': 'المرحلة الرابعة', 'role': 'secretary_id', 'depends_on': ['rn_3_2']},

        {'code': 'rn_5_1', 'name': '1- إصدار تعهد الإشراف', 'stage': 'المرحلة الخامسة', 'role': 'secretary_id', 'depends_on':['rn_4_1', 'rn_4_2', 'rn_4_3', 'rn_4_4', 'rn_4_5']},
        {'code': 'rn_5_2', 'name': '2- الإشراف على التنفيذ', 'stage': 'المرحلة الخامسة', 'role': 'structural_id', 'depends_on': ['rn_5_1']},
        {'code': 'rn_5_3', 'name': '3- كتب البنك', 'stage': 'المرحلة الخامسة', 'role': 'secretary_id', 'depends_on': ['rn_5_2']},
        {'code': 'rn_5_4', 'name': '4- إنهاء الإشراف', 'stage': 'المرحلة الخامسة', 'role': 'secretary_id', 'depends_on': ['rn_5_3']},
    ],

    # 2. غير سكني (استثماري، صناعي، إلخ) + بناء جديد
    'non_res_new':[
        {'code': 'nrn_1_1', 'name': '1- تصميم الكروكي', 'stage': 'المرحلة الأولى', 'role': 'architect_id', 'depends_on': []},
        {'code': 'nrn_1_2', 'name': '2- تجميع المستندات', 'stage': 'المرحلة الأولى', 'role': 'secretary_id', 'depends_on':[]},
        {'code': 'nrn_1_3', 'name': '3- العقد وتحصيل الدفعة الأولى', 'stage': 'المرحلة الأولى', 'role': 'accountant_id', 'depends_on':[]},
        {'code': 'nrn_1_4', 'name': '4- تجهيز النماذج والتعهدات والتوقيع', 'stage': 'المرحلة الأولى', 'role': 'secretary_id', 'depends_on':[]},
        {'code': 'nrn_1_5', 'name': '5- فحص التربة - كتاب الكهرباء', 'stage': 'المرحلة الأولى', 'role': 'secretary_id', 'depends_on':[]},

        {'code': 'nrn_2_1', 'name': '1- سيستم الأعمدة', 'stage': 'المرحلة الثانية', 'role': 'structural_id', 'depends_on': ['nrn_1_1']},
        {'code': 'nrn_2_2', 'name': '2- الواجهات', 'stage': 'المرحلة الثانية', 'role': 'facade_draftsman_id', 'depends_on': ['nrn_1_1']},
        {'code': 'nrn_2_3', 'name': '3- رسم مخطط البلدية', 'stage': 'المرحلة الثانية', 'role': 'muni_draftsman_id', 'depends_on':['nrn_2_1']},

        {'code': 'nrn_3_1', 'name': '1- إرسال للمطافي', 'stage': 'المرحلة الثالثة', 'role': 'secretary_id', 'depends_on': ['nrn_2_3']},
        {'code': 'nrn_3_2', 'name': '2- اعتماد المطافي', 'stage': 'المرحلة الثالثة', 'role': 'secretary_id', 'depends_on': ['nrn_3_1']},
        {'code': 'nrn_3_3', 'name': '3- إرسال للتنظيم', 'stage': 'المرحلة الثالثة', 'role': 'secretary_id', 'depends_on':['nrn_3_2']},
        {'code': 'nrn_3_4', 'name': '4- اعتماد التنظيم', 'stage': 'المرحلة الثالثة', 'role': 'secretary_id', 'depends_on': ['nrn_3_3']},
        {'code': 'nrn_3_5', 'name': '5- إرسال للبلدية', 'stage': 'المرحلة الثالثة', 'role': 'secretary_id', 'depends_on': ['nrn_3_4']},
        {'code': 'nrn_3_6', 'name': '6- اعتماد البلدية', 'stage': 'المرحلة الثالثة', 'role': 'secretary_id', 'depends_on':['nrn_3_5']},
        {'code': 'nrn_3_7', 'name': '7- تحصيل الدفعة الأخيرة من العقد', 'stage': 'المرحلة الثالثة', 'role': 'accountant_id', 'depends_on': ['nrn_3_6']},

        {'code': 'nrn_4_1', 'name': '1- تصميم المخطط الإنشائي', 'stage': 'المرحلة الرابعة', 'role': 'structural_id', 'depends_on':['nrn_3_6']},
        {'code': 'nrn_4_2', 'name': '2- تصميم مخطط الصحي', 'stage': 'المرحلة الرابعة', 'role': 'draftsman_id', 'depends_on': ['nrn_3_6']},
        {'code': 'nrn_4_3', 'name': '5- تجهيز الكراسة النهائية', 'stage': 'المرحلة الرابعة', 'role': 'secretary_id', 'depends_on': ['nrn_3_6']},

        {'code': 'nrn_5_1', 'name': '1- إصدار تعهد الإشراف', 'stage': 'المرحلة الخامسة', 'role': 'secretary_id', 'depends_on':['nrn_4_1', 'nrn_4_2', 'nrn_4_3']},
        {'code': 'nrn_5_2', 'name': '2- الإشراف على التنفيذ', 'stage': 'المرحلة الخامسة', 'role': 'structural_id', 'depends_on':['nrn_5_1']},
        {'code': 'nrn_5_3', 'name': '4- إنهاء الإشراف', 'stage': 'المرحلة الخامسة', 'role': 'secretary_id', 'depends_on': ['nrn_5_2']},
    ],

    # 3. سكن خاص + تعديل واضافة
    'res_add':[
        {'code': 'ra_1_1', 'name': '1- دراسة المخطط الإنشائي القديم', 'stage': 'المرحلة الأولى', 'role': 'structural_id', 'depends_on': []},
        {'code': 'ra_1_2', 'name': '2- كشف على العقار', 'stage': 'المرحلة الأولى', 'role': 'architect_id', 'depends_on':[]},
        {'code': 'ra_1_3', 'name': '3- كروكي', 'stage': 'المرحلة الأولى', 'role': 'architect_id', 'depends_on':[]},
        {'code': 'ra_1_4', 'name': '4- جمع الوثائق والمستندات', 'stage': 'المرحلة الأولى', 'role': 'secretary_id', 'depends_on':[]},
        {'code': 'ra_1_5', 'name': '5- العقد وتحصيل الدفعة الأولى', 'stage': 'المرحلة الأولى', 'role': 'accountant_id', 'depends_on':[]},

        {'code': 'ra_2_1', 'name': '1- سيستم الأعمدة', 'stage': 'المرحلة الثانية', 'role': 'structural_id', 'depends_on':['ra_1_3']},
        {'code': 'ra_2_2', 'name': '2- رسم البلدية', 'stage': 'المرحلة الثانية', 'role': 'muni_draftsman_id', 'depends_on': ['ra_1_3']},

        {'code': 'ra_3_1', 'name': '1- إرسال للبلدية', 'stage': 'المرحلة الثالثة', 'role': 'secretary_id', 'depends_on': ['ra_2_2']},
        {'code': 'ra_3_2', 'name': '2- اعتماد البلدية', 'stage': 'المرحلة الثالثة', 'role': 'secretary_id', 'depends_on': ['ra_3_1']},
        {'code': 'ra_3_3', 'name': '3- تحصيل الدفعة الأخيرة من العقد', 'stage': 'المرحلة الثالثة', 'role': 'accountant_id', 'depends_on': ['ra_3_2']},

        {'code': 'ra_4_1', 'name': '1- مخطط إنشائي كامل', 'stage': 'المرحلة الرابعة', 'role': 'structural_id', 'depends_on': ['ra_3_2']},
        {'code': 'ra_4_2', 'name': '2- تجهيز الكراسة النهائية', 'stage': 'المرحلة الرابعة', 'role': 'secretary_id', 'depends_on': ['ra_3_2']},

        {'code': 'ra_5_1', 'name': '1- الإشراف على التنفيذ', 'stage': 'المرحلة الخامسة', 'role': 'structural_id', 'depends_on':['ra_4_1', 'ra_4_2']},
        {'code': 'ra_5_2', 'name': '2- كتب البنك', 'stage': 'المرحلة الخامسة', 'role': 'secretary_id', 'depends_on': ['ra_5_1']},
        {'code': 'ra_5_3', 'name': '3- إنهاء الإشراف', 'stage': 'المرحلة الخامسة', 'role': 'secretary_id', 'depends_on': ['ra_5_2']},
    ],

    # 4. غير سكني (استثماري، صناعي، إلخ) + تعديل واضافة
    'non_res_add':[
        {'code': 'nra_1_1', 'name': '1- دراسة المخطط الإنشائي القديم', 'stage': 'المرحلة الأولى', 'role': 'structural_id', 'depends_on': []},
        {'code': 'nra_1_2', 'name': '2- كشف على العقار', 'stage': 'المرحلة الأولى', 'role': 'architect_id', 'depends_on':[]},
        {'code': 'nra_1_3', 'name': '3- كروكي', 'stage': 'المرحلة الأولى', 'role': 'architect_id', 'depends_on':[]},
        {'code': 'nra_1_4', 'name': '4- جمع الوثائق والمستندات', 'stage': 'المرحلة الأولى', 'role': 'secretary_id', 'depends_on':[]},
        {'code': 'nra_1_5', 'name': '5- العقد وتحصيل الدفعة الأولى', 'stage': 'المرحلة الأولى', 'role': 'accountant_id', 'depends_on':[]},

        {'code': 'nra_2_1', 'name': '1- سيستم الأعمدة', 'stage': 'المرحلة الثانية', 'role': 'structural_id', 'depends_on': ['nra_1_3']},
        {'code': 'nra_2_2', 'name': '2- رسم البلدية', 'stage': 'المرحلة الثانية', 'role': 'muni_draftsman_id', 'depends_on': ['nra_1_3']},

        {'code': 'nra_3_1', 'name': '1- إرسال للمطافي', 'stage': 'المرحلة الثالثة', 'role': 'secretary_id', 'depends_on':['nra_2_2']},
        {'code': 'nra_3_2', 'name': '2- اعتماد المطافي', 'stage': 'المرحلة الثالثة', 'role': 'secretary_id', 'depends_on': ['nra_3_1']},
        {'code': 'nra_3_3', 'name': '3- إرسال للتنظيم', 'stage': 'المرحلة الثالثة', 'role': 'secretary_id', 'depends_on': ['nra_3_2']},
        {'code': 'nra_3_4', 'name': '4- اعتماد التنظيم', 'stage': 'المرحلة الثالثة', 'role': 'secretary_id', 'depends_on':['nra_3_3']},
        {'code': 'nra_3_5', 'name': '5- إرسال للبلدية', 'stage': 'المرحلة الثالثة', 'role': 'secretary_id', 'depends_on': ['nra_3_4']},
        {'code': 'nra_3_6', 'name': '6- اعتماد البلدية', 'stage': 'المرحلة الثالثة', 'role': 'secretary_id', 'depends_on': ['nra_3_5']},
        {'code': 'nra_3_7', 'name': '7- تحصيل الدفعة الأخيرة من العقد', 'stage': 'المرحلة الثالثة', 'role': 'accountant_id', 'depends_on':['nra_3_6']},

        {'code': 'nra_4_1', 'name': '1- مخطط إنشائي كامل', 'stage': 'المرحلة الرابعة', 'role': 'structural_id', 'depends_on': ['nra_3_6']},
        {'code': 'nra_4_2', 'name': '2- تجهيز الكراسة النهائية', 'stage': 'المرحلة الرابعة', 'role': 'secretary_id', 'depends_on': ['nra_3_6']},

        {'code': 'nra_5_1', 'name': '1- الإشراف على التنفيذ', 'stage': 'المرحلة الخامسة', 'role': 'structural_id', 'depends_on': ['nra_4_1', 'nra_4_2']},
        {'code': 'nra_5_2', 'name': '3- إنهاء الإشراف', 'stage': 'المرحلة الخامسة', 'role': 'secretary_id', 'depends_on': ['nra_5_1']},
    ],

    # 5. هدم (لكل أنواع المباني)
    'demolition':[
        {'code': 'dem_1_1', 'name': '1- تجميع المستندات والوثائق', 'stage': 'المرحلة الأولى', 'role': 'secretary_id', 'depends_on': []},
        {'code': 'dem_1_2', 'name': '2- العقد وتحصيل الدفعة الأولى', 'stage': 'المرحلة الأولى', 'role': 'accountant_id', 'depends_on':[]},
        {'code': 'dem_1_3', 'name': '3- توقيع نماذج البلدية', 'stage': 'المرحلة الأولى', 'role': 'secretary_id', 'depends_on':[]},
        {'code': 'dem_1_4', 'name': '4- كتاب المواصفات وكتاب قطع تربة', 'stage': 'المرحلة الأولى', 'role': 'architect_id', 'depends_on':[]},

        {'code': 'dem_2_1', 'name': '1- إرسال للبلدية', 'stage': 'المرحلة الثانية', 'role': 'secretary_id', 'depends_on': ['dem_1_4']},
        {'code': 'dem_2_2', 'name': '2- اعتماد البلدية', 'stage': 'المرحلة الثانية', 'role': 'secretary_id', 'depends_on': ['dem_2_1']},

        {'code': 'dem_3_1', 'name': '1- الإشراف على الهدم', 'stage': 'المرحلة الثالثة', 'role': 'structural_id', 'depends_on': ['dem_2_2']},
        {'code': 'dem_3_2', 'name': '2- إنهاء الإشراف', 'stage': 'المرحلة الثالثة', 'role': 'secretary_id', 'depends_on': ['dem_3_1']},
    ]
}

# ==============================================================================
#  DOCUMENT SUBTASKS CONFIGURATION
# ==============================================================================

def _get_document_subtasks(building_type, service_type):
    if building_type == 'residential' and service_type == 'shades_garden':
        return[
            'الوثيقة', 'المدنيات', 'ورقة من الكهرباء تفيد دفع المبالغ او الفاتوره',
            'رخصه بناء للقسيمه', 'صور القسيمه', 'صور الحديقه',
        ]
    elif building_type == 'residential' and service_type == 'demolition':
        return[
            'وثيقه الملكية', 'المدنيات', 'كتاب من وزاره الكهرباء و الماء قطع الكيبل',
            'كتاب براةه ذمه من وزاره المواصلات', 'صور وجهات القسيمه',
        ]
    elif building_type == 'cooperative':
        return['كتاب التخصيص', 'المخطط المساحي', 'مدنيه', 'كتب التفويض من وزاره الأرقام الأليه']
    elif building_type == 'commercial':
        return['كتاب التخصيص', 'المخطط المساحي', 'مدنيه', 'كتب التفويض من وزاره الأرقام الأليه']
    else:
        return['الوثيقه', 'المدنيه', 'الموقع العام']


# ==============================================================================
#  STRUCTURAL PLAN SUBTASKS CONFIGURATION
# ==============================================================================

def _get_structural_plan_subtasks(building_type):
    if building_type == 'residential':
        return[
            'مرحلة الحفر', 'مرحلة القواعد والشناجات', 'مرحلة حوائط السرداب',
            'مرحلة صب سقف السرداب', 'مرحلة اعمده الدور الارضى', 'مرحلة صب سقف الدور الارضى',
            'مرحلة اعمده الدور الاول', 'مرحلة صب سقف الدور الاول', 'مرحلة اعمده الدور الثانى',
            'مرحلة صب سقف الدور الثانى', 'مرحلة اعمده الدور السطح', 'مرحله صب سقف السطح',
        ]
    elif building_type == 'commercial':
        return[
            'مرحله القواعد والشناجات', 'مرحله حوائط السرداب', 'مرحله صب سقف السرداب',
            'مرحله اعمده الدور الارضى', 'مرحله صب سقف الدور الارضى', 'مرحله اعمده الدور الاول',
            'مرحله صب سقف الدور الاول', 'مرحله اعمده الدور الثانى', 'مرحله صب سقف الدور الثانى',
            'مرحله اعمده الدور السطح', 'مرحله صب سقف السطح',
        ]
    else:
        return[]


# ==============================================================================
#  HELPER FUNCTIONS FOR GOVERNORATE & REGION
# ==============================================================================
def _get_governorate_areas():
    return {
        'محافظة العاصمة':[
            ('جابر الاحمد', 'جابر الاحمد'), ('القبلة', 'القبلة'), ('الشرق', 'الشرق'),
            ('المرقاب', 'المرقاب'), ('الصالحية', 'الصالحية'), ('دسمان', 'دسمان'),
            ('الدعية', 'الدعية'), ('الدسمة', 'الدسمة'), ('كيفان', 'كيفان'),
            ('الخالدية', 'الخالدية'), ('الشامية', 'الشامية'), ('الروضة', 'الروضة'),
            ('العديلية', 'العديلية'), ('الفيحاء', 'الفيحاء'), ('القادسية', 'القادسية'),
            ('قرطبة', 'قرطبة'), ('السرة', 'السرة'), ('اليرموك', 'اليرموك'),
            ('النزهة', 'النزهة'), ('الشويخ الصناعية 1', 'الشويخ الصناعية 1'),
            ('الشويخ الصناعية 2', 'الشويخ الصناعية 2'), ('الشويخ الصناعية 3', 'الشويخ الصناعية 3'),
            ('الشويخ الادارية', 'الشويخ الادارية'), ('الشويخ السكنى', 'الشويخ السكنى'),
            ('الشويخ التعليمية', 'الشويخ التعليمية'), ('الشويخ الصحيه', 'الشويخ الصحيه'),
            ('الواجهه البحرية', 'الواجهه البحرية'), ('غرناطة', 'غرناطة'),
            ('الصليبيخات', 'الصليبيخات'), ('المنصورية', 'المنصورية'),
            ('الدوحة السكنيه', 'الدوحة السكنيه'), ('الرى', 'الرى'),
            ('ميناء الدوحة', 'ميناء الدوحة'), ('جزيره عوهه', 'جزيره عوهه'),
            ('جزيره فيلكه', 'جزيره فيلكه'), ('جزيره مسكان', 'جزيره مسكان'),
            ('حدائق السور – الحزام الاخضر', 'حدائق السور – الحزام الاخضر'),
            ('بنيد القار', 'بنيد القار'), ('ميناء الشويخ', 'ميناء الشويخ'),
            ('معسكرات المباركيه – جيوان', 'معسكرات المباركيه – جيوان'),
            ('شاليهات الدوحة', 'شاليهات الدوحة'), ('السره', 'السره'),
        ],
        'محافظة حولي':[
            ('حولي', 'حولي'), ('السالمية', 'السالمية'), ('الرميثية', 'الرميثية'),
            ('الجابرية', 'الجابرية'), ('بيان', 'بيان'), ('مشرف', 'مشرف'),
            ('سلوى', 'سلوى'), ('ميدان حولي', 'ميدان حولي'), ('الزهراء', 'الزهراء'),
            ('الصديق', 'الصديق'), ('حطين', 'حطين'), ('السلام', 'السلام'),
            ('الشهداء', 'الشهداء'), ('انجفة', 'انجفة'), ('الشعب', 'الشعب'),
            ('مبارك العبد الله', 'مبارك العبد الله'), ('الواجهه البحريه', 'الواجهه البحريه'),
            ('الضاحيه الدبلوماسيه', 'الضاحيه الدبلوماسيه'),
            ('المباركيه قطعة 15 بيان', 'المباركيه قطعة 15 بيان'), ('البدع', 'البدع'),
        ],
        'محافظة الفروانية':[
            ('الفروانية', 'الفروانية'), ('خيطان', 'خيطان'), ('العمرية', 'العمرية'),
            ('الرحاب', 'الرحاب'), ('الرقعى', 'الرقعى'), ('الشدادية', 'الشدادية'),
            ('الضجيج', 'الضجيج'), ('المطار', 'المطار'), ('غرب الجليب الشداديه', 'غرب الجليب الشداديه'),
            ('عبد الله المبارك', 'عبد الله المبارك'), ('مدينه صباح السالم الجامعية', 'مدينه صباح السالم الجامعية'),
            ('منطقة المعارض جنوب خيطان', 'منطقة المعارض جنوب خيطان'),
            ('الأندلس', 'الأندلس'), ('إشبيلية', 'إشبيلية'), ('جليب الشيوخ', 'جليب الشيوخ'),
            ('الفردوس', 'الفردوس'), ('صباح الناصر', 'صباح الناصر'), ('الرابية', 'الرابية'),
            ('العارضية', 'العارضية'), ('العارضية استعمالات حكومية', 'العارضية استعمالات حكومية'),
            ('العارضية مخازن', 'العارضية مخازن'), ('العارضية الحرفية', 'العارضية الحرفية'),
            ('غرب عبد المبارك السكنى', 'غرب عبد المبارك السكنى'),
            ('جنوب عبد الله المبارك السكنى', 'جنوب عبد الله المبارك السكنى'),
            ('العباسية', 'العباسية'),
        ],
        'محافظة الأحمدي':[
            ('الأحمدي', 'الأحمدي'), ('الفحيحيل', 'الفحيحيل'), ('المنقف', 'المنقف'),
            ('أبو حليفة', 'أبو حليفة'), ('الصباحية', 'الصباحية'), ('الرقة', 'الرقة'),
            ('هدية', 'هدية'), ('الفنطاس', 'الفنطاس'), ('المهبولة', 'المهبولة'),
            ('العقيلة', 'العقيلة'), ('الظهر', 'الظهر'), ('جابر العلي', 'جابر العلي'),
            ('صباح الأحمد السكنية', 'صباح الأحمد السكنية'), ('الوفرة', 'الوفرة'),
            ('الخيران', 'الخيران'), ('ميناء الزور', 'ميناء الزور'),
            ('ميناء عبد الله الصناعية', 'ميناء عبد الله الصناعية'),
            ('ميناء عبد الله', 'ميناء عبد الله'), ('مزارع الوفره', 'مزارع الوفره'),
            ('صباح الاحمد البحريه', 'صباح الاحمد البحريه'),
            ('قردان والحفيرة والفوار', 'قردان والحفيرة والفوار'), ('فهد الاحمد', 'فهد الاحمد'),
            ('على صباح السالم – ام الهيمان', 'على صباح السالم – ام الهيمان'),
            ('عريفجان', 'عريفجان'), ('ضليع الزنيف', 'ضليع الزنيف'),
            ('شرق الاحمدى الخدميه والحرفية والتجاريه', 'شرق الاحمدى الخدميه والحرفية والتجاريه'),
            ('شرق الاحمدى', 'شرق الاحمدى'), ('شاليهات ميناء عبد الله', 'شاليهات ميناء عبد الله'),
            ('شاليهات بنيدر', 'شاليهات بنيدر'), ('شاليهات النويصيب', 'شاليهات النويصيب'),
            ('شاليهات الضاعيه', 'شاليهات الضاعيه'), ('شاليهات الزور', 'شاليهات الزور'),
            ('شاليهات الخيران', 'شاليهات الخيران'), ('شاليهات الجليعه', 'شاليهات الجليعه'),
            ('رجم خشمان ومصلان', 'رجم خشمان ومصلان'), ('جنوب الصباحية', 'جنوب الصباحية'),
            ('برقان', 'برقان'), ('الوفره السكنيه', 'الوفره السكنيه'),
            ('الهيئة العامة للزراعة والثورة السمكيه – مزارع', 'الهيئة العامة للزراعة والثورة السمكيه – مزارع'),
            ('النويصيب', 'النويصيب'), ('المقوع', 'المقوع'), ('العبدليه', 'العبدليه'),
            ('الصناعية الصناعية الخلط الجاهز', 'الصناعية الصناعية الخلط الجاهز'),
            ('الشعيبة الصناعية الشرقيه', 'الشعيبة الصناعية الشرقيه'),
            ('الشعيبة الصناعية الغربيه', 'الشعيبة الصناعية الغربيه'),
            ('الشعيبة', 'الشعيبة'), ('الشدادية الصناعية', 'الشدادية الصناعية'),
            ('الزور وصوله', 'الزور وصوله'), ('ام حجول', 'ام حجول'),
            ('ام قدير', 'ام قدير'), ('ابو خرجين والصبيحية', 'ابو خرجين والصبيحية'),
        ],
        'محافظة الجهراء':[
            ('الجهراء', 'الجهراء'), ('القصر', 'القصر'), ('النسيم', 'النسيم'),
            ('الواحة', 'الواحة'), ('النعيم', 'النعيم'), ('تيماء', 'تيماء'),
            ('سعد العبدالله', 'سعد العبدالله'), ('الصليبية', 'الصليبية'),
            ('كبد', 'كبد'), ('المطلاع', 'المطلاع'), ('أمغرة', 'أمغرة'),
            ('البحيث', 'البحيث'), ('الجهراء الصناعية الثانية', 'الجهراء الصناعية الثانية'),
            ('الجهراء الصناعية الحرفيه الاولى', 'الجهراء الصناعية الحرفيه الاولى'),
            ('الرتقة والحريجه', 'الرتقة والحريجه'), ('الرحية وام توينج', 'الرحية وام توينج'),
            ('الروضتين', 'الروضتين'), ('السالمى', 'السالمى'), ('السكراب', 'السكراب'),
            ('الشقايا – الدبدبة – المتياهه', 'الشقايا – الدبدبة – المتياهه'),
            ('الصابرية – العرفجية', 'الصابرية – العرفجية'), ('الصبية', 'الصبية'),
            ('الصليبية الزراعية', 'الصليبية الزراعية'), ('الصليبيه السكنية', 'الصليبيه السكنية'),
            ('الصليبية الصناعية 2', 'الصليبية الصناعية 2'), ('الصليبيه الصناعية 1', 'الصليبيه الصناعية 1'),
            ('الصير وام المدفاع', 'الصير وام المدفاع'), ('العبدلى', 'العبدلى'),
            ('العبدلى وصخيبريات', 'العبدلى وصخيبريات'), ('العيون', 'العيون'),
            ('القيروان – جنوب الدوحة', 'القيروان – جنوب الدوحة'),
            ('المستثمر الاجنبى (منطقة العبدلى الاقتصادية )', 'المستثمر الاجنبى (منطقة العبدلى الاقتصادية )'),
            ('المطلاع وجال الاطراف', 'المطلاع وجال الاطراف'), ('النعايم الصناعية', 'النعايم الصناعية'),
            ('النهضة – شرق الصليبخات', 'النهضة – شرق الصليبخات'), ('امغره الصناعية', 'امغره الصناعية'),
            ('جال الزور', 'جال الزور'), ('جزيرة ام المرادم', 'جزيرة ام المرادم'),
            ('جزيره ام النمل', 'جزيره ام النمل'), ('جزيرة بوبيان', 'جزيرة بوبيان'),
            ('جزيرة قارووه', 'جزيرة قارووه'), ('جزيرة كبر', 'جزيرة كبر'),
            ('جزيرة وربة', 'جزيرة وربة'), ('جنوب امغرة', 'جنوب امغرة'),
            ('شرق الجهراء', 'شرق الجهراء'), ('شرق تيماء', 'شرق تيماء'),
            ('شمال غرب الجهراء', 'شمال غرب الجهراء'), ('قلمة شايع والمناقيش', 'قلمة شايع والمناقيش'),
            ('كاظمة', 'كاظمة'), ('كبد والشق والضبعة', 'كبد والشق والضبعة'),
            ('معسكرات الجهراء', 'معسكرات الجهراء'), ('مقبرة', 'مقبرة'),
            ('مناطق نائية -الجهراء', 'مناطق نائية -الجهراء'),
        ],
        'محافظة مبارك الكبير':[
            ('مبارك الكبير', 'مبارك الكبير'), ('العدان', 'العدان'),
            ('القرين', 'القرين'), ('القصور', 'القصور'), ('المسيلة', 'المسيلة'),
            ('غرب أبو فطيرة', 'غرب أبو فطيرة'), ('الفنيطيس', 'الفنيطيس'),
            ('المسايل', 'المسايل'), ('الوسطى', 'الوسطى'),
            ('جنوب الوسطى', 'جنوب الوسطى'), ('صباح السالم', 'صباح السالم'),
            ('صبحان الصناعية', 'صبحان الصناعية'), ('ضاحية ابو فطيرة', 'ضاحية ابو فطيرة'),
            ('ابو الحصانية', 'ابو الحصانية'),
        ],
    }

def _get_all_regions():
    all_regions =[]
    seen_regions = set()
    for areas in _get_governorate_areas().values():
        for area_val, area_label in areas:
            if area_val not in seen_regions:
                all_regions.append((area_val, area_label))
                seen_regions.add(area_val)
    return sorted(all_regions, key=lambda x: x[1])


# ==============================================================================
#  SALE ORDER MODEL
# ==============================================================================
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    building_type = fields.Selection([
        ('residential', 'سكن خاص'), ('investment', 'استثماري'), ('commercial', 'تجاري'),
        ('industrial', 'صناعي'), ('cooperative', 'جمعيات وتعاونيات'), ('mosque', 'مساجد'),
        ('hangar', 'مخازن / شبرات'), ('farm', 'مزارع')
    ], string="نوع العقار")
    service_type = fields.Selection([
        ('new_construction', 'بناء جديد'), ('demolition', 'هدم'), ('modification', 'تعديل'),
        ('addition', 'اضافة'), ('addition_modification', 'تعديل واضافة'),
        ('supervision_only', 'إشراف هندسي فقط'), ('renovation', 'ترميم'),
        ('internal_partitions', 'قواطع داخلية'), ('shades_garden', 'مظلات / حدائق')
    ], string="نوع الخدمة")

    plot_no = fields.Char(string="رقم القسيمة")
    block_no = fields.Char(string="القطعة")
    street_no = fields.Char(string="الضاحيه")
    area = fields.Char(string="مساحة الارض")

    project_id = fields.Many2one('project.project', string='Project', copy=False)

    quotation_stage_id = fields.Many2one(
        'engineering.quotation.stage',
        string='Quotation Stage',
        tracking=True,
        default=lambda self: self.env['engineering.quotation.stage'].search([], order='sequence', limit=1)
    )
    stage_history_ids = fields.One2many('engineering.quotation.stage.history', 'quotation_id', string='Stage History')

    next_stage_button_name = fields.Char(compute='_compute_next_stage_button_name')
    show_next_stage_button = fields.Boolean(compute='_compute_next_stage_button_name')

    required_documents = fields.Html(string="المستندات المطلوبة", compute='_compute_required_documents', store=True)

    @api.depends('service_type', 'building_type')
    def _compute_required_documents(self):
        for order in self:
            docs = "<ul>"
            docs += "<li>البطاقة المدنية للمالك (Civil ID Copy)</li>"
            if order.service_type == 'new_construction':
                docs += "<li>وثيقة الملكية</li><li>كتاب التخصيص</li><li>مخطط المساحة</li>"
            elif order.service_type in['modification', 'addition', 'addition_modification']:
                docs += "<li>رخصة البناء الأصلية</li><li>المخططات المرخصة</li><li>وثيقة البيت</li>"
            elif order.service_type == 'demolition':
                docs += "<li>كتاب براءة ذمة من الكهرباء والماء</li><li>رخصة البناء القديمة</li>"
            docs += "</ul>"
            order.required_documents = docs

    def action_confirm(self):
        for order in self:
            if order.signature:
                approved_stage = self.env['engineering.quotation.stage'].search([('is_approved_stage', '=', True)], limit=1)
                if approved_stage and order.quotation_stage_id != approved_stage:
                    order.quotation_stage_id = approved_stage.id
        return super(SaleOrder, self).action_confirm()

    def action_move_to_next_stage(self):
        self.ensure_one()
        current_stage = self.quotation_stage_id
        next_stage = current_stage.next_stage_id if current_stage else False
        if next_stage:
            self.env['engineering.quotation.stage.history'].create({
                'quotation_id': self.id,
                'from_stage_id': current_stage.id if current_stage else False,
                'to_stage_id': next_stage.id,
            })
            self.write({'quotation_stage_id': next_stage.id})

            if next_stage.is_approved_stage:
                if not self.project_id:
                    self._create_engineering_project()

                if self.project_id and not self.project_id.workflow_started:
                    self.project_id.action_start_workflow()

                return {'effect': {'fadeout': 'slow', 'message': _('تمت الموافقة وتم إنشاء المشروع والمهام بنجاح!'), 'type': 'rainbow_man'}}
            return {'type': 'ir.actions.client', 'tag': 'reload'}
        return True

    def action_create_project_from_quotation(self):
        self.ensure_one()
        if self.project_id:
            return
        project = self._create_engineering_project()
        return {
            'type': 'ir.actions.act_window',
            'name': _('المشروع (Project)'),
            'res_model': 'project.project',
            'res_id': project.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def _create_engineering_project(self):
        self.ensure_one()
        gov_id = getattr(self, 'governorate_id', False)
        reg_id = getattr(self, 'region_id', False)
        elec = getattr(self, 'electricity_receipt', False)
        civil_no = getattr(self, 'civil_number', False) # <-- تم استدعاء الرقم المدني هنا
        
        project_vals = {
            'name': f"{self.name} - {self.partner_id.name or ''}",
            'partner_id': self.partner_id.id,
            'sale_order_id': self.id,
            'building_type': self.building_type,
            'service_type': self.service_type,
            'plot_no': self.plot_no,
            'block_no': self.block_no,
            'street_no': self.street_no,
            'area': self.area,
            'governorate_id': gov_id.id if gov_id else False,
            'region_id': reg_id.id if reg_id else False,
            'electricity_receipt': elec,
            'civil_number': civil_no, # <-- تم نقل الرقم المدني للمشروع هنا
            'engineering_package_id': self.engineering_package_id.id if self.engineering_package_id else False,
        }
        project = self.env['project.project'].create(project_vals)
        project._get_project_stages_map()
        self.write({'project_id': project.id})
        return project

    @api.depends('quotation_stage_id', 'state')
    def _compute_next_stage_button_name(self):
        for order in self:
            order.show_next_stage_button = bool(order.quotation_stage_id.next_stage_id and order.state != 'cancel')
            order.next_stage_button_name = order.quotation_stage_id.button_name

    def action_send_quotation_whatsapp(self):
        self.ensure_one()
        phone = self.partner_id.mobile or self.partner_id.phone
        if not phone:
            raise UserError(_("رقم الهاتف مفقود"))
        self._portal_ensure_token()
        link = self.env['ir.config_parameter'].sudo().get_param('web.base.url') + self.get_portal_url()
        msg = urllib.parse.quote(_("مرحباً %s، يرجى مراجعة عرض السعر %s: %s") % (self.partner_id.name, self.name, link))
        return {'type': 'ir.actions.act_url', 'url': f"https://web.whatsapp.com/send?phone={phone}&text={msg}", 'target': 'new'}

    def action_create_opening_fee_invoice(self):
        self.ensure_one()
        product_fee = self.env['product.product'].search([('name', '=', 'رسوم فتح ملف')], limit=1)
        if not product_fee:
            product_fee = self.env['product.product'].create({'name': 'رسوم فتح ملف', 'type': 'service', 'list_price': 50.0})
        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.partner_id.id,
            'invoice_date': fields.Date.today(),
            'invoice_line_ids':[(0, 0, {'product_id': product_fee.id, 'quantity': 1, 'price_unit': 50.0, 'name': 'رسوم فتح ملف وتصميم مبدئي'})],
        }
        invoice = self.env['account.move'].create(invoice_vals)
        return {'name': _('Open Invoice'), 'view_mode': 'form', 'res_model': 'account.move', 'res_id': invoice.id, 'type': 'ir.actions.act_window'}

    def action_apply_opening_deduction(self):
        self.ensure_one()
        product_fee = self.env['product.product'].search([('name', '=', 'رسوم فتح ملف')], limit=1)
        if not product_fee:
            raise UserError(_("Product 'رسوم فتح ملف' not found."))
        self.env['sale.order.line'].create({
            'order_id': self.id,
            'product_id': product_fee.id,
            'name': 'خصم رسوم فتح ملف',
            'product_uom_qty': 1,
            'price_unit': -50.0,
            'tax_id': False,
        })
        return True


class EngineeringQuotationStage(models.Model):
    _name = 'engineering.quotation.stage'
    _description = 'Engineering Quotation Stage'
    _order = 'sequence, id'

    name = fields.Char(string='اسم المرحلة', required=True, translate=True)
    sequence = fields.Integer(default=10)
    next_stage_id = fields.Many2one('engineering.quotation.stage', string="المرحلة التالية")
    button_name = fields.Char(string="نص الزر")
    is_approved_stage = fields.Boolean(string="مرحلة الموافقة؟")
    is_rejected_stage = fields.Boolean(string="مرحلة الرفض؟")
    fold = fields.Boolean(string='Folded in Kanban', default=False)


class EngineeringQuotationStageHistory(models.Model):
    _name = 'engineering.quotation.stage.history'
    _description = 'Quotation Stage History'
    _order = 'change_date desc'

    quotation_id = fields.Many2one('sale.order', string='Quotation', ondelete='cascade')
    from_stage_id = fields.Many2one('engineering.quotation.stage', string='From Stage')
    to_stage_id = fields.Many2one('engineering.quotation.stage', string='To Stage')
    changed_by_id = fields.Many2one('res.users', string='Changed By', default=lambda self: self.env.user)
    change_date = fields.Datetime(string='Change Date', default=fields.Datetime.now)


# ==============================================================================
#  PROJECT MODEL
# ==============================================================================
class ProjectProject(models.Model):
    _inherit = 'project.project'

    sale_order_id = fields.Many2one('sale.order', string='Source Quotation', readonly=True)
    building_type = fields.Selection([
        ('residential', 'سكن خاص'), ('investment', 'استثماري'), ('commercial', 'تجاري'),
        ('industrial', 'صناعي'), ('cooperative', 'جمعيات وتعاونيات'), ('mosque', 'مساجد'),
        ('hangar', 'مخازن / شبرات'), ('farm', 'مزارع')
    ], string="نوع المبنى")
    service_type = fields.Selection([
        ('new_construction', 'بناء جديد'), ('demolition', 'هدم'), ('modification', 'تعديل'),
        ('addition', 'اضافة'), ('addition_modification', 'تعديل واضافة'),
        ('supervision_only', 'إشراف هندسي فقط'), ('renovation', 'ترميم'),
        ('internal_partitions', 'قواطع داخلية'), ('shades_garden', 'مظلات / حدائق')
    ], string="نوع الخدمة")

    governorate_id = fields.Many2one('kuwait.governorate', string="المحافظة")
    region_id = fields.Many2one('kuwait.region', string="المنطقة")

    @api.onchange('governorate_id')
    def _onchange_governorate(self):
        self.region_id = False

    @api.constrains('governorate_id', 'region_id')
    def _check_valid_region(self):
        for project in self:
            gov_name = project.governorate_id.name if project.governorate_id else False
            region_name = project.region_id.name if project.region_id else False
            if gov_name and region_name:
                valid_regions = [area[0] for area in _get_governorate_areas().get(gov_name,[])]
                if region_name not in valid_regions:
                    raise ValidationError(_("المنطقة المختارة '%s' لا تتبع للمحافظة '%s'.") % (region_name, gov_name))

    plot_no = fields.Char(string="رقم القسيمة")
    block_no = fields.Char(string="القطعة")
    street_no = fields.Char(string="الضاحيه")
    area = fields.Char(string="المساحة (Area)")
    electricity_receipt = fields.Char(string="ايصال تيار كهربا")

    architect_id = fields.Many2one('res.users', string="المهندس المعماري")
    accountant_id = fields.Many2one('res.users', string="المحاسبة")
    structural_id = fields.Many2one('res.users', string="المهندس الإنشائي")
    facade_draftsman_id = fields.Many2one('res.users', string="رسام الواجهات")
    secretary_id = fields.Many2one('res.users', string="السكرتارية")
    muni_draftsman_id = fields.Many2one('res.users', string="رسام البلدية")
    electrical_id = fields.Many2one('res.users', string="مهندس الكهرباء")
    draftsman_id = fields.Many2one('res.users', string="الرسام (صحي/مخططات)")

    workflow_started = fields.Boolean(default=False)

    commitment_ids = fields.Many2many('sale.order.line', string='Commitments', copy=False)

    def _get_project_stages_map(self):
        self.ensure_one()
        stages = self.env['project.task.type'].search([('project_ids', 'in', self.id)], order='sequence')
        stage_map = {stage.name: stage.id for stage in stages}

        required_stages =[
            'المرحلة الأولى', 'المرحلة الثانية', 'المرحلة الثالثة',
            'المرحلة الرابعة', 'المرحلة الخامسة'
        ]

        for idx, s_name in enumerate(required_stages):
            if s_name not in stage_map:
                exist_stage = self.env['project.task.type'].search([('name', '=', s_name)], limit=1)
                if exist_stage:
                    exist_stage.sudo().write({'project_ids': [(4, self.id)]})
                    stage_map[s_name] = exist_stage.id
                else:
                    new_stage = self.env['project.task.type'].sudo().create({
                        'name': s_name,
                        'project_ids':[(4, self.id)],
                        'sequence': idx + 1
                    })
                    stage_map[s_name] = new_stage.id

        return stage_map

    def _get_workflow_key(self):
        self.ensure_one()
        if self.service_type == 'demolition':
            return 'demolition'

        is_addition = self.service_type in['addition', 'modification', 'addition_modification']
        if self.building_type == 'residential':
            return 'res_add' if is_addition else 'res_new'
        else:
            return 'non_res_add' if is_addition else 'non_res_new'

    def action_start_workflow(self):
        self.ensure_one()
        if self.workflow_started:
            raise UserError(_("تم بدء سير العمل مسبقاً!"))

        wf_key = self._get_workflow_key()
        workflow = WORKFLOW_TEMPLATES.get(wf_key,[])
        if not workflow:
            raise UserError(_("لا توجد خطة مهام مطابقة لنوع الخدمة والمبنى."))

        self._get_project_stages_map()

        for step in workflow:
            is_disabled_task = bool(step.get('depends_on'))
            self._create_task_for_step(step, is_disabled=is_disabled_task)

        self.workflow_started = True
        self._trigger_next_workflow_step()

    def _trigger_next_workflow_step(self, completed_code=False, **kwargs):
        self.ensure_one()

        wf_key = self._get_workflow_key()
        workflow = WORKFLOW_TEMPLATES.get(wf_key, [])
        if not workflow:
            return

        tasks = self.env['project.task'].search([('project_id', '=', self.id)])
        task_states = {t.workflow_step: t.state for t in tasks if t.workflow_step}

        for task in tasks.filtered(lambda t: t.is_disabled and t.workflow_step):
            step_template = next((s for s in workflow if s['code'] == task.workflow_step), None)

            if step_template:
                depends_on = step_template.get('depends_on',[])

                if not depends_on:
                    task.is_disabled = False
                    continue

                all_dependencies_met = all(task_states.get(dep_code) == '03_approved' for dep_code in depends_on)

                if all_dependencies_met:
                    task.is_disabled = False

    def _create_task_for_step(self, step_data, is_disabled=False):
        stages_map = self._get_project_stages_map()
        stage_id = stages_map.get(step_data['stage'])
        if not stage_id:
            return

        wf_key = self._get_workflow_key()
        workflow = WORKFLOW_TEMPLATES.get(wf_key,[])

        tasks_in_current_stage = [t for t in workflow if t['stage'] == step_data['stage']]
        task_sequence = 10
        for index, t in enumerate(tasks_in_current_stage):
            if t['code'] == step_data['code']:
                task_sequence = index + 1
                break

        user_record = getattr(self, step_data['role'], False)
        user_id = user_record.id if user_record else False

        val = {
            'name': step_data['name'],
            'project_id': self.id,
            'stage_id': stage_id,
            'workflow_step': step_data['code'],
            'sequence': task_sequence,
            'is_disabled': is_disabled,
        }
        if user_id:
            val['user_ids'] = [(4, user_id)]

        new_task = self.env['project.task'].create(val)

        subtask_base_vals = {
            'project_id': self.id,
            'parent_id': new_task.id,
            'stage_id': stage_id,
            'is_disabled': False,
        }

        task_name_lower = step_data['name'].strip()
        is_document_task = (
            "تجميع المستندات" in task_name_lower
            or "جمع الوثائق" in task_name_lower
            or "تجميع المستندات والوثائق" in task_name_lower
        )

        if is_document_task:
            doc_subtasks = _get_document_subtasks(self.building_type, self.service_type)
            for sub_name in doc_subtasks:
                vals = subtask_base_vals.copy()
                vals['name'] = sub_name
                self.env['project.task'].create(vals)

        if "فحص التربة" in step_data['name'] and "الكهرباء" in step_data['name']:
            for sub_name in[
                "فحص التربه تم الأرسال",
                "فحص التربه تم الأعتماد",
                "الكهرباء تم الأرسال",
                "الكهرباء تم الأعتماد",
            ]:
                vals = subtask_base_vals.copy()
                vals['name'] = sub_name
                self.env['project.task'].create(vals)

        is_structural_plan_task = (
            "المخطط الإنشائي" in step_data['name']
            or "المخطط الانشائي" in step_data['name']
            or "مخطط إنشائي" in step_data['name']
            or "مخطط انشائي" in step_data['name']
        )

        if is_structural_plan_task:
            structural_subtasks = _get_structural_plan_subtasks(self.building_type)
            for sub_name in structural_subtasks:
                vals = subtask_base_vals.copy()
                vals['name'] = sub_name
                self.env['project.task'].create(vals)


# ==============================================================================
#  PROJECT TASK MODEL
# ==============================================================================
class ProjectTask(models.Model):
    _inherit = 'project.task'
    state = fields.Selection([
        ('01_in_progress', 'In Progress (قيد التنفيذ)'),
        ('02_changes_requested', 'Changes Requested (مطلوب تعديلات)'),
        ('03_approved', 'Approved (معتمد)'),
    ], string='Status', default='01_in_progress', tracking=True)
    
    workflow_step = fields.Char(string="Workflow Trigger", readonly=True)
    is_disabled = fields.Boolean(string="مقفلة (Disabled)", default=False)
    phase_ids = fields.One2many('project.task.phase', 'task_id', string='مراحل التنفيذ (Phases)')

    sketch_ids = fields.One2many('project.task.sketch', 'task_id', string="Sketches")
    sketch_count = fields.Integer(compute='_compute_sketch_count', string="Number of Sketches")

    is_paperwork_task = fields.Boolean(string="Is Paperwork Task", compute="_compute_task_category", store=False)
    is_engineering_task = fields.Boolean(string="Is Engineering Task", compute="_compute_task_category", store=False)

    @api.depends('workflow_step')
    def _compute_task_category(self):
        for task in self:
            is_paper = False
            is_eng = False

            if task.workflow_step:
                role = False
                for wf_list in WORKFLOW_TEMPLATES.values():
                    for step in wf_list:
                        if step['code'] == task.workflow_step:
                            role = step.get('role')
                            break
                    if role:
                        break

                if role in ['secretary_id', 'accountant_id']:
                    is_paper = True
                elif role in['structural_id', 'facade_draftsman_id', 'muni_draftsman_id', 'architect_id', 'electrical_id', 'draftsman_id']:
                    is_eng = True
                else:
                    is_paper = True
                    is_eng = True
            else:
                is_paper = True
                is_eng = True

            task.is_paperwork_task = is_paper
            task.is_engineering_task = is_eng

    @api.depends('sketch_ids')
    def _compute_sketch_count(self):
        for task in self:
            task.sketch_count = len(task.sketch_ids)

    proof_attachment_ids = fields.Many2many(
        'ir.attachment',
        'project_task_ir_attachments_rel',
        'task_id',
        'attachment_id',
        string="اثباتات (Attachments)"
    )

    def action_load_default_phases(self):
        self.ensure_one()

        if self.is_disabled:
            raise UserError(_("لا يمكن تحميل المراحل لمهمة مقفلة."))

        if self.phase_ids:
            return

        seq = 10
        phases_data =[
            ('مرحله الحفر', 'عام (General)'),
            ('مرحله القواعد والشناجات', 'عام (General)'),
            ('مرحله حوائط السرداب', 'السرداب (Basement)'),
            ('مرحله صب سقف السرداب', 'السرداب (Basement)'),
            ('مرحله اعمده الدور الارضى', 'الدور الأرضي (Ground)'),
            ('مرحله صب سقف الدور الارضى', 'الدور الأرضي (Ground)'),
            ('مرحله اعمده الدور الاول', 'الدور الأول (First)'),
            ('مرحله صب سقف الدور الاول', 'الدور الأول (First)'),
            ('مرحله اعمده الدور الثانى', 'الدور الثاني (Second)'),
            ('مرحله صب سقف الدور الثانى', 'الدور الثاني (Second)'),
            ('مرحله اعمده الدور السطح', 'السطح (Roof)'),
            ('مرحله صب سقف السطح', 'السطح (Roof)'),
        ]

        phases_to_create =[]
        for name, category in phases_data:
            phases_to_create.append((0, 0, {
                'name': name,
                'floor_category': category,
                'sequence': seq
            }))
            seq += 10

        self.write({'phase_ids': phases_to_create})

    def get_completed_phases_grouped(self):
        self.ensure_one()
        completed_phases = self.phase_ids.filtered(lambda p: p.is_completed)

        grouped = {}
        for phase in completed_phases:
            cat = phase.floor_category
            if cat not in grouped:
                grouped[cat] = []
            grouped[cat].append(phase)
        return grouped

    def write(self, vals):
        if 'stage_id' in vals or vals.get('state') in ['1_done', '03_approved']:
            for task in self:
                if task.is_disabled and task.workflow_step and not task.parent_id and vals.get('is_disabled') is not False:
                    raise UserError(_("لا يمكنك إنجاز هذه المهمة أو تغيير حالتها لأنها مقفلة! يرجى الانتهاء من المهام السابقة أولاً."))

        res = super(ProjectTask, self).write(vals)

        for task in self:
            is_done = False

            if vals.get('state') in['03_approved']:
                is_done = True

            elif 'stage_id' in vals:
                stage = self.env['project.task.type'].browse(vals['stage_id'])
                if stage.fold or stage.is_closed or 'done' in (stage.name or '').lower() or 'منجز' in (stage.name or ''):
                    is_done = True
                else:
                    done_stage = self.env.ref('project.project_stage_3', raise_if_not_found=False)
                    if done_stage and stage.id == done_stage.id:
                        is_done = True

            if is_done and task.workflow_step and task.project_id:
                task.project_id._trigger_next_workflow_step()

        return res

    def action_view_parent_project(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.project',
            'res_id': self.project_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_send_task_form_whatsapp(self):
        self.ensure_one()
        if self.is_disabled:
            raise UserError(_("لا يمكن إرسال نموذج مهمة مقفلة."))

        phone = self.project_id.partner_id.mobile or self.project_id.partner_id.phone
        if not phone:
            raise UserError("رقم الهاتف مفقود للعميل في المشروع")

        cleaned_phone = ''.join(filter(str.isdigit, phone))
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        self.sudo()._portal_ensure_token()
        token = self.sudo().access_token if hasattr(self, 'access_token') else ''

        if token:
            project_url = (
                f"{base_url}/report/pdf/engineering_project.report_initial_design_template"
                f"/{self.id}?access_token={token}"
            )
        else:
            project_url = (
                f"{base_url}/report/pdf/engineering_project.report_initial_design_template/{self.id}"
            )

        message = _("مرحباً %s،\nنرفق لكم نموذج مكونات المشروع للمراجعة.\nالرابط:\n%s") % (
            self.project_id.partner_id.name, project_url
        )
        encoded_message = urllib.parse.quote(message)
        whatsapp_url = f"https://web.whatsapp.com/send?phone={cleaned_phone}&text={encoded_message}"
        return {'type': 'ir.actions.act_url', 'url': whatsapp_url, 'target': 'new'}

    def action_send_project_form_pdf_whatsapp(self):
        self.ensure_one()

        if self.is_disabled:
            raise UserError(_("لا يمكن إرسال نموذج مهمة مقفلة."))

        allowed_steps =['rn_1_1', 'nrn_1_1', 'ra_1_3', 'nra_1_3']
        if self.workflow_step not in allowed_steps:
            raise UserError(_("هذا الزر متاح فقط لمهام تصميم الكروكي."))

        partner = self.project_id.partner_id
        if not partner:
            raise UserError(_("لا يوجد عميل مرتبط بالمشروع."))

        phone = partner.mobile or partner.phone
        if not phone:
            raise UserError(_("لا يوجد رقم هاتف للعميل: %s") % partner.name)

        cleaned_phone = ''.join(filter(str.isdigit, phone))
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        task_sudo = self.sudo()
        if hasattr(task_sudo, '_portal_ensure_token'):
            task_sudo._portal_ensure_token()

        token = task_sudo.access_token if hasattr(task_sudo, 'access_token') else ''

        if token:
            pdf_url = (
                f"{base_url}/report/pdf/engineering_project.report_initial_design_template"
                f"/{self.id}?access_token={token}"
            )
        else:
            pdf_url = (
                f"{base_url}/report/pdf/engineering_project.report_initial_design_template/{self.id}"
            )

        message = _(
            "مرحباً %s،\n"
            "نرفق لكم نموذج مكونات المشروع الخاص بمشروعكم للمراجعة والاطلاع.\n\n"
            "رابط النموذج:\n%s\n\n"
            "شركة الهندسة المعمارية"
        ) % (partner.name, pdf_url)

        encoded_message = urllib.parse.quote(message)
        whatsapp_url = f"https://web.whatsapp.com/send?phone={cleaned_phone}&text={encoded_message}"

        return {
            'type': 'ir.actions.act_url',
            'url': whatsapp_url,
            'target': 'new',
        }

    def action_create_new_sketch(self):
        self.ensure_one()
        new_sketch = self.env['project.task.sketch'].create({
            'task_id': self.id,
        })
        return {
            'name': _('Sketch Editor'),
            'type': 'ir.actions.act_window',
            'res_model': 'project.task.sketch',
            'view_mode': 'form',
            'res_id': new_sketch.id,
            'target': 'new',
        }

    @api.model
    def _send_periodic_task_reminders(self):
        open_tasks = self.search([
            ('stage_id.fold', '=', False),
            ('user_ids', '!=', False),
            ('is_disabled', '=', False)
        ])

        user_task_counts = {}
        for task in open_tasks:
            for user in task.user_ids:
                if user not in user_task_counts:
                    user_task_counts[user] = 0
                user_task_counts[user] += 1

        for user, count in user_task_counts.items():
            if count > 0:
                message = f"""
                <div style="direction: rtl; text-align: right;">
                    <strong>مرحباً {user.name}،</strong><br/>
                    هذا تذكير تلقائي بأن لديك <b>{count} مهام</b> قيد التنفيذ بانتظرك.<br/>
                    يرجى مراجعة قائمة المهام الخاصة بك وإنجازها.
                </div>
                """
                user.partner_id.message_post(
                    body=message,
                    subject="تذكير بالمهام (Task Reminder)",
                    message_type='notification',
                    subtype_xmlid='mail.mt_comment',
                    author_id=self.env.ref('base.partner_root').id,
                )


# ==============================================================================
#  NEW MODEL: project.task.sketch
# ==============================================================================
class ProjectTaskSketch(models.Model):
    _name = 'project.task.sketch'
    _description = 'Project Task Sketch'
    _order = 'create_date desc'

    task_id = fields.Many2one('project.task', string='Task', ondelete='cascade', required=True)
    name = fields.Char(string='Sketch Name', required=True, default=lambda self: _('New Sketch %s') % datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
    sketch_image = fields.Binary(string="Sketch Image", attachment=True)
    created_by_id = fields.Many2one('res.users', string='Created By', default=lambda self: self.env.user, readonly=True)
    create_date = fields.Datetime(string='Creation Date', readonly=True)

    def action_open_sketch_editor(self):
        self.ensure_one()
        return {
            'name': _('Sketch Editor'),
            'type': 'ir.actions.act_window',
            'res_model': 'project.task.sketch',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }


# ==============================================================================
#  IR ATTACHMENT MODEL
# ==============================================================================
class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    def action_send_attachment_whatsapp(self):
        self.ensure_one()
        task = self.env['project.task'].search([
            ('proof_attachment_ids', 'in', self.ids)
        ], limit=1)

        if not task:
            raise UserError(_("لا يمكن إيجاد المهمة المرتبطة بهذا المرفق."))

        partner = task.project_id.partner_id
        if not partner:
            raise UserError(_("لا يوجد عميل مرتبط بالمشروع."))

        phone = partner.mobile or partner.phone
        if not phone:
            raise UserError(_("لا يوجد رقم هاتف للعميل: %s") % partner.name)

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        download_url = f"{base_url}/web/content/{self.id}?download=true"

        message = _("مرحباً %s,\n\nيرجى الإطلاع على المرفق الجديد الخاص بمشروعكم:\n%s\n\nالملف: %s") % (partner.name, download_url, self.name)

        encoded_message = urllib.parse.quote(message)
        whatsapp_url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_message}"

        return {
            'type': 'ir.actions.act_url',
            'url': whatsapp_url,
            'target': 'new',
        }


# ==============================================================================
#  GOVERNORATE AND REGION MODELS
# ==============================================================================
class KuwaitGovernorate(models.Model):
    _name = 'kuwait.governorate'
    _description = 'Kuwait Governorate'
    name = fields.Char(string='المحافظة', required=True)


class KuwaitRegion(models.Model):
    _name = 'kuwait.region'
    _description = 'Kuwait Region'
    name = fields.Char(string='المنطقة', required=True)
    governorate_id = fields.Many2one('kuwait.governorate', string="المحافظة", required=True)


class ProjectTaskPhase(models.Model):
    _name = 'project.task.phase'
    _description = 'Task Construction Phase Checklist'
    _order = 'sequence, id'

    task_id = fields.Many2one('project.task', string='Task', ondelete='cascade')
    sequence = fields.Integer(string='التسلسل', default=10)
    floor_category = fields.Char(string='الدور (Floor)', required=True)
    name = fields.Text(string='المرحلة (Phase)', required=True)
    is_completed = fields.Boolean(string='تم (Completed)', default=False)