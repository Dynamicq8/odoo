# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import datetime
import urllib.parse

# ==============================================================================
#  WORKFLOW TEMPLATES (خرائط سير العمل)
# ==============================================================================
WORKFLOW_TEMPLATES = {
    # 1. سكن خاص + بناء جديد
    'res_new':[
        {'code': 'rn_1_1', 'name': '1- تصميم الكروكي', 'stage': 'المرحلة الأولى', 'role': 'architect_id'},
        {'code': 'rn_1_2', 'name': '2- تجميع المستندات', 'stage': 'المرحلة الأولى', 'role': 'secretary_id'},
        {'code': 'rn_1_3', 'name': '3- العقد وتحصيل الدفعة الأولى', 'stage': 'المرحلة الأولى', 'role': 'accountant_id'},
        {'code': 'rn_1_4', 'name': '4- تجهيز النماذج والتعهدات والتوقيع', 'stage': 'المرحلة الأولى', 'role': 'secretary_id'},
        {'code': 'rn_1_5', 'name': '5- فحص التربة - كتاب الكهرباء', 'stage': 'المرحلة الأولى', 'role': 'secretary_id'},
        
        {'code': 'rn_2_1', 'name': '1- سيستم الأعمدة', 'stage': 'المرحلة الثانية', 'role': 'structural_id'},
        {'code': 'rn_2_2', 'name': '2- الواجهات', 'stage': 'المرحلة الثانية', 'role': 'facade_draftsman_id'},
        {'code': 'rn_2_3', 'name': '3- رسم مخطط البلدية', 'stage': 'المرحلة الثانية', 'role': 'muni_draftsman_id'},
        
        {'code': 'rn_3_1', 'name': '1- إرسال للبلدية', 'stage': 'المرحلة الثالثة', 'role': 'secretary_id'},
        {'code': 'rn_3_2', 'name': '2- اعتماد البلدية', 'stage': 'المرحلة الثالثة', 'role': 'secretary_id'},
        {'code': 'rn_3_3', 'name': '3- تحصيل الدفعة الأخيرة من العقد', 'stage': 'المرحلة الثالثة', 'role': 'accountant_id'},
        
        {'code': 'rn_4_1', 'name': '1- تصميم المخطط الإنشائي', 'stage': 'المرحلة الرابعة', 'role': 'structural_id'},
        {'code': 'rn_4_2', 'name': '2- تصميم مخطط الصحي', 'stage': 'المرحلة الرابعة', 'role': 'draftsman_id'},
        {'code': 'rn_4_3', 'name': '3- تصميم مخطط الكهرباء', 'stage': 'المرحلة الرابعة', 'role': 'electrical_id'},
        {'code': 'rn_4_4', 'name': '4- تصميم مخطط الفرش', 'stage': 'المرحلة الرابعة', 'role': 'architect_id'},
        {'code': 'rn_4_5', 'name': '5- تجهيز الكراسة النهائية', 'stage': 'المرحلة الرابعة', 'role': 'secretary_id'},
        
        {'code': 'rn_5_1', 'name': '1- إصدار تعهد الإشراف', 'stage': 'المرحلة الخامسة', 'role': 'secretary_id'},
        {'code': 'rn_5_2', 'name': '2- الإشراف على التنفيذ', 'stage': 'المرحلة الخامسة', 'role': 'structural_id'},
        {'code': 'rn_5_3', 'name': '3- كتب البنك', 'stage': 'المرحلة الخامسة', 'role': 'secretary_id'},
        {'code': 'rn_5_4', 'name': '4- إنهاء الإشراف', 'stage': 'المرحلة الخامسة', 'role': 'secretary_id'},
    ],
    
    # 2. غير سكني (استثماري، صناعي، إلخ) + بناء جديد
    'non_res_new':[
        {'code': 'nrn_1_1', 'name': '1- تصميم الكروكي', 'stage': 'المرحلة الأولى', 'role': 'architect_id'},
        {'code': 'nrn_1_2', 'name': '2- تجميع المستندات', 'stage': 'المرحلة الأولى', 'role': 'secretary_id'},
        {'code': 'nrn_1_3', 'name': '3- العقد وتحصيل الدفعة الأولى', 'stage': 'المرحلة الأولى', 'role': 'accountant_id'},
        {'code': 'nrn_1_4', 'name': '4- تجهيز النماذج والتعهدات والتوقيع', 'stage': 'المرحلة الأولى', 'role': 'secretary_id'},
        {'code': 'nrn_1_5', 'name': '5- فحص التربة - كتاب الكهرباء', 'stage': 'المرحلة الأولى', 'role': 'secretary_id'},
        
        {'code': 'nrn_2_1', 'name': '1- سيستم الأعمدة', 'stage': 'المرحلة الثانية', 'role': 'structural_id'},
        {'code': 'nrn_2_2', 'name': '2- الواجهات', 'stage': 'المرحلة الثانية', 'role': 'facade_draftsman_id'},
        {'code': 'nrn_2_3', 'name': '3- رسم مخطط البلدية', 'stage': 'المرحلة الثانية', 'role': 'muni_draftsman_id'},
        
        {'code': 'nrn_3_1', 'name': '1- إرسال للمطافي', 'stage': 'المرحلة الثالثة', 'role': 'secretary_id'},
        {'code': 'nrn_3_2', 'name': '2- اعتماد المطافي', 'stage': 'المرحلة الثالثة', 'role': 'secretary_id'},
        {'code': 'nrn_3_3', 'name': '3- إرسال للتنظيم', 'stage': 'المرحلة الثالثة', 'role': 'secretary_id'},
        {'code': 'nrn_3_4', 'name': '4- اعتماد التنظيم', 'stage': 'المرحلة الثالثة', 'role': 'secretary_id'},
        {'code': 'nrn_3_5', 'name': '5- إرسال للبلدية', 'stage': 'المرحلة الثالثة', 'role': 'secretary_id'},
        {'code': 'nrn_3_6', 'name': '6- اعتماد البلدية', 'stage': 'المرحلة الثالثة', 'role': 'secretary_id'},
        {'code': 'nrn_3_7', 'name': '7- تحصيل الدفعة الأخيرة من العقد', 'stage': 'المرحلة الثالثة', 'role': 'accountant_id'},
        
        {'code': 'nrn_4_1', 'name': '1- تصميم المخطط الإنشائي', 'stage': 'المرحلة الرابعة', 'role': 'structural_id'},
        {'code': 'nrn_4_2', 'name': '2- تصميم مخطط الصحي', 'stage': 'المرحلة الرابعة', 'role': 'draftsman_id'},
        {'code': 'nrn_4_3', 'name': '5- تجهيز الكراسة النهائية', 'stage': 'المرحلة الرابعة', 'role': 'secretary_id'},
        
        {'code': 'nrn_5_1', 'name': '1- إصدار تعهد الإشراف', 'stage': 'المرحلة الخامسة', 'role': 'secretary_id'},
        {'code': 'nrn_5_2', 'name': '2- الإشراف على التنفيذ', 'stage': 'المرحلة الخامسة', 'role': 'structural_id'},
        {'code': 'nrn_5_3', 'name': '4- إنهاء الإشراف', 'stage': 'المرحلة الخامسة', 'role': 'secretary_id'},
    ],
    
    # 3. سكن خاص + تعديل واضافة
    'res_add':[
        {'code': 'ra_1_1', 'name': '1- دراسة المخطط الإنشائي القديم', 'stage': 'المرحلة الأولى', 'role': 'structural_id'},
        {'code': 'ra_1_2', 'name': '2- كشف على العقار', 'stage': 'المرحلة الأولى', 'role': 'architect_id'},
        {'code': 'ra_1_3', 'name': '3- كروكي', 'stage': 'المرحلة الأولى', 'role': 'architect_id'},
        {'code': 'ra_1_4', 'name': '4- جمع الوثائق والمستندات', 'stage': 'المرحلة الأولى', 'role': 'secretary_id'},
        {'code': 'ra_1_5', 'name': '5- العقد وتحصيل الدفعة الأولى', 'stage': 'المرحلة الأولى', 'role': 'accountant_id'},
        
        {'code': 'ra_2_1', 'name': '1- سيستم الأعمدة', 'stage': 'المرحلة الثانية', 'role': 'structural_id'},
        {'code': 'ra_2_2', 'name': '2- رسم البلدية', 'stage': 'المرحلة الثانية', 'role': 'muni_draftsman_id'},
        
        {'code': 'ra_3_1', 'name': '1- إرسال للبلدية', 'stage': 'المرحلة الثالثة', 'role': 'secretary_id'},
        {'code': 'ra_3_2', 'name': '2- اعتماد البلدية', 'stage': 'المرحلة الثالثة', 'role': 'secretary_id'},
        {'code': 'ra_3_3', 'name': '3- تحصيل الدفعة الأخيرة من العقد', 'stage': 'المرحلة الثالثة', 'role': 'accountant_id'},
        
        {'code': 'ra_4_1', 'name': '1- مخطط إنشائي كامل', 'stage': 'المرحلة الرابعة', 'role': 'structural_id'},
        {'code': 'ra_4_2', 'name': '2- تجهيز الكراسة النهائية', 'stage': 'المرحلة الرابعة', 'role': 'secretary_id'},
        
        {'code': 'ra_5_1', 'name': '1- الإشراف على التنفيذ', 'stage': 'المرحلة الخامسة', 'role': 'structural_id'},
        {'code': 'ra_5_2', 'name': '2- كتب البنك', 'stage': 'المرحلة الخامسة', 'role': 'secretary_id'},
        {'code': 'ra_5_3', 'name': '3- إنهاء الإشراف', 'stage': 'المرحلة الخامسة', 'role': 'secretary_id'},
    ],
    
    # 4. غير سكني (استثماري، صناعي، إلخ) + تعديل واضافة
    'non_res_add':[
        {'code': 'nra_1_1', 'name': '1- دراسة المخطط الإنشائي القديم', 'stage': 'المرحلة الأولى', 'role': 'structural_id'},
        {'code': 'nra_1_2', 'name': '2- كشف على العقار', 'stage': 'المرحلة الأولى', 'role': 'architect_id'},
        {'code': 'nra_1_3', 'name': '3- كروكي', 'stage': 'المرحلة الأولى', 'role': 'architect_id'},
        {'code': 'nra_1_4', 'name': '4- جمع الوثائق والمستندات', 'stage': 'المرحلة الأولى', 'role': 'secretary_id'},
        {'code': 'nra_1_5', 'name': '5- العقد وتحصيل الدفعة الأولى', 'stage': 'المرحلة الأولى', 'role': 'accountant_id'},
        
        {'code': 'nra_2_1', 'name': '1- سيستم الأعمدة', 'stage': 'المرحلة الثانية', 'role': 'structural_id'},
        {'code': 'nra_2_2', 'name': '2- رسم البلدية', 'stage': 'المرحلة الثانية', 'role': 'muni_draftsman_id'},
        
        {'code': 'nra_3_1', 'name': '1- إرسال للمطافي', 'stage': 'المرحلة الثالثة', 'role': 'secretary_id'},
        {'code': 'nra_3_2', 'name': '2- اعتماد المطافي', 'stage': 'المرحلة الثالثة', 'role': 'secretary_id'},
        {'code': 'nra_3_3', 'name': '3- إرسال للتنظيم', 'stage': 'المرحلة الثالثة', 'role': 'secretary_id'},
        {'code': 'nra_3_4', 'name': '4- اعتماد التنظيم', 'stage': 'المرحلة الثالثة', 'role': 'secretary_id'},
        {'code': 'nra_3_5', 'name': '5- إرسال للبلدية', 'stage': 'المرحلة الثالثة', 'role': 'secretary_id'},
        {'code': 'nra_3_6', 'name': '6- اعتماد البلدية', 'stage': 'المرحلة الثالثة', 'role': 'secretary_id'},
        {'code': 'nra_3_7', 'name': '7- تحصيل الدفعة الأخيرة من العقد', 'stage': 'المرحلة الثالثة', 'role': 'accountant_id'},
        
        {'code': 'nra_4_1', 'name': '1- مخطط إنشائي كامل', 'stage': 'المرحلة الرابعة', 'role': 'structural_id'},
        {'code': 'nra_4_2', 'name': '2- تجهيز الكراسة النهائية', 'stage': 'المرحلة الرابعة', 'role': 'secretary_id'},
        
        {'code': 'nra_5_1', 'name': '1- الإشراف على التنفيذ', 'stage': 'المرحلة الخامسة', 'role': 'structural_id'},
        {'code': 'nra_5_2', 'name': '3- إنهاء الإشراف', 'stage': 'المرحلة الخامسة', 'role': 'secretary_id'},
    ],
    
    # 5. هدم (لكل أنواع المباني) NEW WORKFLOW ADDED
    'demolition':[
        {'code': 'dem_1_1', 'name': '1- تجميع المستندات والوثائق', 'stage': 'المرحلة الأولى', 'role': 'secretary_id'},
        {'code': 'dem_1_2', 'name': '2- العقد وتحصيل الدفعة الأولى', 'stage': 'المرحلة الأولى', 'role': 'accountant_id'},
        {'code': 'dem_1_3', 'name': '3- توقيع نماذج البلدية', 'stage': 'المرحلة الأولى', 'role': 'secretary_id'},
        {'code': 'dem_1_4', 'name': '4- كتاب المواصفات وكتاب قطع تربة', 'stage': 'المرحلة الأولى', 'role': 'architect_id'},
        
        {'code': 'dem_2_1', 'name': '1- إرسال للبلدية', 'stage': 'المرحلة الثانية', 'role': 'secretary_id'},
        {'code': 'dem_2_2', 'name': '2- اعتماد البلدية', 'stage': 'المرحلة الثانية', 'role': 'secretary_id'},
        
        {'code': 'dem_3_1', 'name': '1- الإشراف على الهدم', 'stage': 'المرحلة الثالثة', 'role': 'structural_id'},
        {'code': 'dem_3_2', 'name': '2- إنهاء الإشراف', 'stage': 'المرحلة الثالثة', 'role': 'secretary_id'},
    ]
}

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
            ('الضجيج', 'الضجيج'), ('المطار', 'المطار'),
            ('غرب الجليب الشداديه', 'غرب الجليب الشداديه'),
            ('عبد الله المبارك', 'عبد الله المبارك'),
            ('مدينه صباح السالم الجامعية', 'مدينه صباح السالم الجامعية'),
            ('منطقة المعارض جنوب خيطان', 'منطقة المعارض جنوب خيطان'),
            ('الأندلس', 'الأندلس'), ('إشبيلية', 'إشبيلية'),
            ('جليب الشيوخ', 'جليب الشيوخ'), ('الفردوس', 'الفردوس'),
            ('صباح الناصر', 'صباح الناصر'), ('الرابية', 'الرابية'),
            ('العارضية', 'العارضية'),
            ('العارضية استعمالات حكومية', 'العارضية استعمالات حكومية'),
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
            ('صباح الاحمد السكنيه', 'صباح الاحمد السكنيه'),
            ('صباح الاحمد البحريه', 'صباح الاحمد البحريه'),
            ('قردان والحفيرة والفوار', 'قردان والحفيرة والفوار'),
            ('فهد الاحمد', 'فهد الاحمد'),
            ('على صباح السالم – ام الهيمان', 'على صباح السالم – ام الهيمان'),
            ('عريفجان', 'عريفجان'), ('ضليع الزنيف', 'ضليع الزنيف'),
            ('شرق الاحمدى الخدميه والحرفية والتجاريه', 'شرق الاحمدى الخدميه والحرفية والتجاريه'),
            ('شرق الاحمدى', 'شرق الاحمدى'),
            ('شاليهات ميناء عبد الله', 'شاليهات ميناء عبد الله'),
            ('شاليهات بنيدر', 'شاليهات بنيدر'),
            ('شاليهات النويصيب', 'شاليهات النويصيب'),
            ('شاليهات الضاعيه', 'شاليهات الضاعيه'), ('شاليهات الزور', 'شاليهات الزور'),
            ('شاليهات الخيران', 'شاليهات الخيران'),
            ('شاليهات الجليعه', 'شاليهات الجليعه'),
            ('رجم خشمان ومصلان', 'رجم خشمان ومصلان'),
            ('جنوب الصباحية', 'جنوب الصباحية'), ('برقان', 'برقان'),
            ('الوفره السكنيه', 'الوفره السكنيه'),
            ('الهيئة العامة للزراعة والثورة السمكيه – مزارع', 'الهيئة العامة للزراعة والثورة السمكيه – مزارع'),
            ('النويصيب', 'النويصيب'), ('المقوع', 'المقوع'), ('الفحيحيل', 'الفحيحيل'),
            ('العبدليه', 'العبدليه'),
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
            ('الرتقة والحريجه', 'الرتقة والحريجه'),
            ('الرحية وام توينج', 'الرحية وام توينج'), ('الروضتين', 'الروضتين'),
            ('السالمى', 'السالمى'), ('السكراب', 'السكراب'),
            ('الشقايا – الدبدبة – المتياهه', 'الشقايا – الدبدبة – المتياهه'),
            ('الصابرية – العرفجية', 'الصابرية – العرفجية'),
            ('الصبية', 'الصبية'), ('الصليبية الزراعية', 'الصليبية الزراعية'),
            ('الصليبيه السكنية', 'الصليبيه السكنية'),
            ('الصليبية الصناعية 2', 'الصليبية الصناعية 2'),
            ('الصليبيه الصناعية 1', 'الصليبيه الصناعية 1'),
            ('الصير وام المدفاع', 'الصير وام المدفاع'), ('العبدلى', 'العبدلى'),
            ('العبدلى وصخيبريات', 'العبدلى وصخيبريات'), ('العيون', 'العيون'),
            ('القيروان – جنوب الدوحة', 'القيروان – جنوب الدوحة'),
            ('المستثمر الاجنبى (منطقة العبدلى الاقتصادية )', 'المستثمر الاجنبى (منطقة العبدلى الاقتصادية )'),
            ('المطلاع وجال الاطراف', 'المطلاع وجال الاطراف'),
            ('النعايم الصناعية', 'النعايم الصناعية'),
            ('النهضة – شرق الصليبخات', 'النهضة – شرق الصليبخات'),
            ('امغره الصناعية', 'امغره الصناعية'), ('تيماء', 'تيماء'),
            ('جال الزور', 'جال الزور'), ('جزيرة ام المرادم', 'جزيرة ام المرادم'),
            ('جزيره ام النمل', 'جزيره ام النمل'), ('جزيرة بوبيان', 'جزيرة بوبيان'),
            ('جزيرة قارووه', 'جزيرة قارووه'), ('جزيرة كبر', 'جزيرة كبر'),
            ('جزيرة وربة', 'جزيرة وربة'), ('جنوب امغرة', 'جنوب امغرة'),
            ('شرق الجهراء', 'شرق الجهراء'), ('شرق تيماء', 'شرق تيماء'),
            ('شمال غرب الجهراء', 'شمال غرب الجهراء'),
            ('قلمة شايع والمناقيش', 'قلمة شايع والمناقيش'),
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
            ('صبحان الصناعية', 'صبحان الصناعية'),
            ('ضاحية ابو فطيرة', 'ضاحية ابو فطيرة'), ('ابو الحصانية', 'ابو الحصانية'),
        ],
    }

def _get_all_regions(self):
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

    building_type = fields.Selection([('residential', 'سكن خاص'), ('investment', 'استثماري'), ('commercial', 'تجاري'), ('industrial', 'صناعي'), ('cooperative', 'جمعيات وتعاونيات'), ('mosque', 'مساجد'), ('hangar', 'مخازن / شبرات'), ('farm', 'مزارع')], string="نوع العقار")
    service_type = fields.Selection([('new_construction', 'بناء جديد'), ('demolition', 'هدم'), ('modification', 'تعديل'), ('addition', 'اضافة'), ('addition_modification', 'تعديل واضافة'), ('supervision_only', 'إشراف هندسي فقط'), ('renovation', 'ترميم'), ('internal_partitions', 'قواطع داخلية'), ('shades_garden', 'مظلات / حدائق')], string="نوع الخدمة")

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
            elif order.service_type in ['modification', 'addition', 'addition_modification']:
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
                return {'effect': {'fadeout': 'slow', 'message': _('تمت الموافقة على عرض السعر!'), 'type': 'rainbow_man'}}
            return {'type': 'ir.actions.client', 'tag': 'reload'}
        return True

    def action_create_project_from_quotation(self):
        self.ensure_one()
        if self.project_id: return
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
        project_vals = {
            'name': f"{self.name} - {self.partner_id.name}",
            'partner_id': self.partner_id.id,
            'sale_order_id': self.id,
            'building_type': self.building_type,
            'service_type': self.service_type,
            'plot_no': self.plot_no,
            'block_no': self.block_no,
            'street_no': self.street_no,
            'area': self.area,
            'governorate_id': self.governorate_id.id, 
            'region_id': self.region_id.id,
            'electricity_receipt': self.electricity_receipt, # ADD THIS LINE
        }
        project = self.env['project.project'].create(project_vals)
        
        stages_to_create =[
            'المرحلة الأولى', 
            'المرحلة الثانية', 
            'المرحلة الثالثة', 
            'المرحلة الرابعة', 
            'المرحلة الخامسة'
        ]

        for index, stage_name in enumerate(stages_to_create):
            self.env['project.task.type'].create({
                'name': stage_name, 
                'project_ids': [(4, project.id)], 
                'sequence': index + 1
            })
            
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
        if not phone: raise UserError(_("رقم الهاتف مفقود"))
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
        if not product_fee: raise UserError(_("Product 'رسوم فتح ملف' not found."))
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
    building_type = fields.Selection([('residential', 'سكن خاص'), ('investment', 'استثماري'), ('commercial', 'تجاري'), ('industrial', 'صناعي'), ('cooperative', 'جمعيات وتعاونيات'), ('mosque', 'مساجد'), ('hangar', 'مخازن / شبرات'), ('farm', 'مزارع')], string="نوع المبنى")
    service_type = fields.Selection([('new_construction', 'بناء جديد'), ('demolition', 'هدم'), ('modification', 'تعديل'), ('addition', 'اضافة'), ('addition_modification', 'تعديل واضافة'), ('supervision_only', 'إشراف هندسي فقط'), ('renovation', 'ترميم'), ('internal_partitions', 'قواطع داخلية'), ('shades_garden', 'مظلات / حدائق')], string="نوع الخدمة")
    
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
    triggered_steps = fields.Text(string="المهام المنفذة", default="")
    
    commitment_ids = fields.Many2many('sale.order.line', string='Commitments', copy=False)

    def _get_project_stages_map(self):
        self.ensure_one()
        stages = self.env['project.task.type'].search([('project_ids', 'in', self.id)], order='sequence')
        return {stage.name: stage.id for stage in stages}

    def _get_workflow_key(self):
        self.ensure_one()
        # 1. Check for Demolition First
        if self.service_type == 'demolition':
            return 'demolition'
            
        # 2. Check for Others
        is_addition = self.service_type in ['addition', 'modification', 'addition_modification']
        if self.building_type == 'residential':
            return 'res_add' if is_addition else 'res_new'
        else:
            return 'non_res_add' if is_addition else 'non_res_new'

    def action_start_workflow(self):
        self.ensure_one()
        if self.workflow_started:
            raise UserError(_("تم بدء سير العمل مسبقاً!"))

        wf_key = self._get_workflow_key()
        workflow = WORKFLOW_TEMPLATES.get(wf_key, [])
        if not workflow:
            raise UserError(_("لا توجد خطة مهام مطابقة لنوع الخدمة والمبنى."))

        # إنشاء جميع المهام دفعة واحدة
        for index, step in enumerate(workflow):
            # المهمة الأولى فقط تكون مفعلة (False)، والباقي مقفلة (True)
            is_disabled_task = (index != 0)
            self._create_task_for_step(step, is_disabled=is_disabled_task)

        self.workflow_started = True
        # فقط المهمة الأولى تعتبر "مفعلة" أو "مبدئية" في هذا السياق
        self.triggered_steps = workflow[0]['code'] + "," 

    def _trigger_next_workflow_step(self, completed_code):
        self.ensure_one()
        wf_key = self._get_workflow_key()
        workflow = WORKFLOW_TEMPLATES.get(wf_key, [])

        triggered_steps_list = (self.triggered_steps or "").split(',')
        
        for i, step in enumerate(workflow):
            if step['code'] == completed_code:
                if i + 1 < len(workflow):
                    next_step = workflow[i + 1]
                    # تأكد أن المهمة التالية لم يتم تفعيلها من قبل
                    if next_step['code'] not in triggered_steps_list:
                        # البحث عن المهمة التالية في قاعدة البيانات بناءً على كود الخطوة
                        next_task = self.env['project.task'].search([
                            ('project_id', '=', self.id),
                            ('workflow_step', '=', next_step['code'])
                        ], limit=1)
                        
                        # إذا تم العثور على المهمة، قم بفك القفل عنها
                        if next_task:
                            next_task.is_disabled = False
                            # تحديث قائمة المهام التي تم تفعيلها
                            self.triggered_steps += next_step['code'] + ","
                break

    def _create_task_for_step(self, step_data, is_disabled=False):
        stages_map = self._get_project_stages_map()
        stage_id = stages_map.get(step_data['stage'])
        if not stage_id: 
            return 
        
        # --- FIX: Calculate task Sequence to force 1, 2, 3, 4 sorting from Top to Bottom ---
        wf_key = self._get_workflow_key()
        workflow = WORKFLOW_TEMPLATES.get(wf_key, [])
        tasks_in_current_stage = [t for t in workflow if t['stage'] == step_data['stage']]
        
        task_sequence = 10
        for index, t in enumerate(tasks_in_current_stage):
            if t['code'] == step_data['code']:
                task_sequence = index + 1 # gives sequence 1, 2, 3, 4 to keep order correct.
                break
        # ----------------------------------------------------------------------------------

        user_id = getattr(self, step_data['role']).id if hasattr(self, step_data['role']) and getattr(self, step_data['role']) else False
        
        val = {
            'name': step_data['name'], 
            'project_id': self.id, 
            'stage_id': stage_id,
            'workflow_step': step_data['code'],
            'sequence': task_sequence, # This forces Odoo Kanban to place 1 at the top
            'is_disabled': is_disabled, # تمرير حالة التعطيل هنا
        }
        if user_id: 
            val['user_ids'] = [(4, user_id)]
            
        self.env['project.task'].create(val)


# ==============================================================================
#  PROJECT TASK MODEL
# ==============================================================================
class ProjectTask(models.Model):
    _inherit = 'project.task'

    workflow_step = fields.Char(string="Workflow Trigger", readonly=True)
    
    # حقل جديد لمعرفة إن كانت المهمة مقفلة (بانتظار المهام السابقة) أم لا
    is_disabled = fields.Boolean(string="مقفلة (Disabled)", default=False)

    phase_ids = fields.One2many('project.task.phase', 'task_id', string='مراحل التنفيذ (Phases)')

    def action_load_default_phases(self):
        self.ensure_one() # Ensure action is called on a single task

        if self.is_disabled:
            raise UserError(_("لا يمكن تحميل المراحل لمهمة مقفلة."))

        if self.phase_ids:
            # يمكن إضافة تنبيه للمستخدم هنا إذا كان يرغب في حذف المراحل الحالية وتحميل الافتراضية
            # أو ببساطة عدم فعل أي شيء إذا كانت موجودة بالفعل.
            # for now, we'll just return if phases already exist.
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
        # منع نقل المهمة إلى حالة منجزة إذا كانت مقفلة
        # Assuming 'stage_id' is the field for the task's stage,
        # and 'project.project_stage_3' is the external ID for the 'Done' stage.
        done_stage = self.env.ref('project.project_stage_3', raise_if_not_found=False)

        if 'stage_id' in vals and done_stage and vals['stage_id'] == done_stage.id:
            for task in self:
                if task.is_disabled:
                    raise UserError(_("لا يمكنك إنجاز هذه المهمة لأنها مقفلة! يرجى الانتهاء من المهام السابقة في سير العمل أولاً."))

        res = super(ProjectTask, self).write(vals)

        # إذا تم تحديث حالة المهمة لتصبح منجزة
        # Note: The original code used `vals['state']` which is not a standard field on `project.task` for stage.
        # It should be `vals['stage_id']` checked against the 'Done' stage.
        # The line `done_stage = self.env.ref('project.project_stage_3', raise_if_not_found=False)`
        # needs to be outside the loop if used in the `write` method for performance,
        # or define it once as `done_stage_id` as in the previous suggested code.
        # I'm updating it to use `vals['stage_id']` as standard practice.
        if 'stage_id' in vals and done_stage and vals['stage_id'] == done_stage.id:
            for task in self:
                if task.workflow_step and task.project_id:
                    task.project_id._trigger_next_workflow_step(task.workflow_step)
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
        if not phone: raise UserError("رقم الهاتف مفقود للعميل في المشروع")
        cleaned_phone = ''.join(filter(str.isdigit, phone))
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        self._portal_ensure_token()
        project_url = f"{base_url}/report/pdf/engineering_project.report_initial_design_template/{self.id}"
        message = _("مرحباً %s،\nنرفق لكم نموذج مكونات المشروع للمراجعة.\nالرابط:\n%s") % (self.project_id.partner_id.name, project_url)
        encoded_message = urllib.parse.quote(message)
        whatsapp_url = f"https://web.whatsapp.com/send?phone={cleaned_phone}&text={encoded_message}"
        return { 'type': 'ir.actions.act_url', 'url': whatsapp_url, 'target': 'new' }
        
    @api.model
    def _send_periodic_task_reminders(self):
        open_tasks = self.search([
            ('stage_id.fold', '=', False), 
            ('user_ids', '!=', False),
            ('is_disabled', '=', False) # تجاهل المهام المقفلة في التذكير
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
                    هذا تذكير تلقائي بأن لديك <b>{count} مهام</b> قيد التنفيذ بانتظارك.<br/>
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
    name = fields.Char(string='المرحلة (Phase)', required=True)
    is_completed = fields.Boolean(string='تم (Completed)', default=False)
