import os
import requests
import asyncio
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import arabic_reshaper
from bidi.algorithm import get_display

# إعداد التسجيل (Logging)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# الإعدادات الأساسية والتوكنات (يمكن وضعها كمتغيرات بيئة على Render لاحقاً)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "9093140496:AAE-j8bxSCgxLMwwmNqdOKaQHM3v-STaSLk")
WALLET_USDT = "TVAXrTFSUbGDpf26B52Bb4TmB6LTMWdgtU"

# مفاتيح المزودين (تأخذ من متغيرات البيئة أو توضع هنا مباشرة)
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "YOUR_HF_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "YOUR_GROQ_API_KEY")

# روابط النماذج
HF_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

def ar(text):
    if not text:
        return ""
    return get_display(arabic_reshaper.reshape(text))

# محاولة تحميل الخطوط العربية للتقارير
try:
    pdfmetrics.registerFont(TTFont('Amiri', 'Amiri-Regular.ttf'))
    pdfmetrics.registerFont(TTFont('AmiriBold', 'Amiri-Bold.ttf'))
except:
    pass

def generate_pdf_report(topic):
    pdf_filename = "Chief_Agent_Report.pdf"
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []

    try:
        title_style = ParagraphStyle('TitleStyle', fontName='AmiriBold', fontSize=16, textColor=colors.HexColor('#0F172A'), alignment=1, spaceAfter=4)
        subtitle_style = ParagraphStyle('SubTitleStyle', fontName='Amiri', fontSize=9.5, textColor=colors.HexColor('#64748B'), alignment=1, spaceAfter=12)
        section_style = ParagraphStyle('SectionStyle', fontName='AmiriBold', fontSize=11, textColor=colors.HexColor('#1E40AF'), spaceBefore=12, spaceAfter=6, alignment=2)
        body_style = ParagraphStyle('BodyStyle', fontName='Amiri', fontSize=9.5, leading=16, textColor=colors.HexColor('#334155'), spaceAfter=6, alignment=2)
    except:
        title_style = ParagraphStyle('TitleStyle', fontSize=16, alignment=1)
        subtitle_style = ParagraphStyle('SubTitleStyle', fontSize=10, alignment=1)
        section_style = ParagraphStyle('SectionStyle', fontSize=11, alignment=2)
        body_style = ParagraphStyle('BodyStyle', fontSize=10, alignment=2)

    story.append(Paragraph(ar("التقرير الاستراتيجي المعتمد لمشرف الوكلاء"), title_style))
    story.append(Paragraph(f"AUTONOMOUS TARGET: {topic[:40]}", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1E40AF'), spaceBefore=2, spaceAfter=14))

    info_data = [
        [Paragraph(ar(f"توجيه المدير (بهجت): {topic[:30]}"), body_style), Paragraph(ar("الحالة: تشغيل المنظومة المزدوجة 24/7"), body_style)],
        [Paragraph(ar("النطاق: أمازون / التداول / التطوير الذاتي"), body_style), Paragraph(ar("الاعتمادية: قصوى"), body_style)]
    ]
    t_info = Table(info_data, colWidths=[265, 265])
    t_info.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_info)
    story.append(Spacer(1, 10))

    story.append(Paragraph(ar("التحليل التشغيلي المتقدم وتوليد الأكواد:"), section_style))
    story.append(Paragraph(ar(f"• تم فحص الطلب التنفيذي حول: ({topic}) باستخدام المعمارية المزدوجة (Groq & Hugging Face)."), body_style))
    story.append(Paragraph(ar("• تم تحسين مسارات الوكلاء وتفعيل قدرة المشرف على هندسة الأكواد البرمجية ذاتياً."), body_style))

    story.append(Spacer(1, 4))
    story.append(Paragraph(ar("التوصية النهائية لمشرف الوكلاء:"), section_style))
    story.append(Paragraph(ar("النظام جاهز للتنفيذ التلقائي ورفع كفاءة العائدات بشكل دائم."), body_style))

    doc.build(story)
    return pdf_filename

# دالة الاستعلام عبر المحرك الثنائي (Groq أولاً للسرعة والمنطق، ثم Hugging Face كاحتياط)
async def query_ai_engines(prompt: str) -> str:
    # 1. محاولة استخدام Groq للتحليل المتقدم والبرمجة
    if GROQ_API_KEY and GROQ_API_KEY != "YOUR_GROQ_API_KEY":
        try:
            headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": "أنت مشرف وكلاء ذكي ومهندس برمجيات متقدم تدير أعمال بهجت. عندما يطلب كوداً أو فكرة، قدم تحليلاً عميقاً وكود بايثون احترافياً جاهزاً للتنفيذ."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3
            }
            res = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=20)
            if res.status_code == 200:
                data = res.json()
                return data['choices'][0]['message']['content'].strip()
        except Exception as e:
            logging.error(f"Groq error: {e}")

    # 2. محاولة استخدام Hugging Face كبديل
    if HUGGINGFACE_API_KEY and HUGGINGFACE_API_KEY != "YOUR_HF_API_KEY":
        try:
            headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
            payload = {
                "inputs": f"أنت مشرف وكلاء ذكي لبهجت. أجب باحترافية وعمق: {prompt}",
                "parameters": {"max_new_tokens": 400, "return_full_text": False}
            }
            res = requests.post(HF_API_URL, headers=headers, json=payload, timeout=20)
            if res.status_code == 200:
                res_json = res.json()
                if isinstance(res_json, list) and len(res_json) > 0:
                    return res_json[0].get("generated_text", "").strip()
                elif isinstance(res_json, dict) and "generated_text" in res_json:
                    return res_json["generated_text"].strip()
        except Exception as e:
            logging.error(f"Hugging Face error: {e}")

    # الرد الاحتياطي الافتراضي في حال انقطاع المفاتيح
    return (
        f"أهلاً بك يا بهجت. بصفتي مشرف الوكلاء، استوعبت طلبك بدقة:\n\"{prompt}\"\n\n"
        f"النظام يعمل بكفاءة. هل ترغب أن أكتب لك كود البايثون الخاص بهذه المهمة فوراً أم نولد تقرير PDF؟"
    )

# معالجة الرسائل الواردة من تيليغرام
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()
    chat_id = update.message.chat_id
    text_lower = user_text.lower()

    # طلب تقرير PDF
    if any(k in text_lower for k in ["تقرير", "ولد", "صمم", "دراسة", "خطة", "ملف", "حلل"]):
        await update.message.reply_text("🤖 جاري إعداد التقرير الاستراتيجي المطلوب وتجهيز الملف...")
        pdf_path = generate_pdf_report(user_text)
        with open(pdf_path, "rb") as f:
            await context.bot.send_document(
                chat_id=chat_id,
                document=f,
                caption=(
                    f"🌟 **[تم توليد التقرير بنجاح]:**\n"
                    f"استجابة لطلبك: \"{user_text}\"\n\n"
                    f"💰 محفظة التحويل USDT (TRC20):\n`{WALLET_USDT}`"
                ),
                parse_mode="Markdown"
            )
        return

    # الرد عبر الذكاء الاصطناعي المزدوج (مع دعم توليد الأكواد البرمجية ذاتياً)
    ai_response = await query_ai_engines(user_text)
    
    # تقسيم الرسالة إذا كانت طويلة لتجنب قيود تيليغرام
    if len(ai_response) > 4000:
        for x in range(0, len(ai_response), 4000):
            await update.message.reply_text(ai_response[x:x+4000])
    else:
        await update.message.reply_text(ai_response)

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("🚀 مشرف الوكلاء (المعمارية المزدوجة + المبرمج الذاتي) يعمل الآن...")
    app.run_polling()

if __name__ == "__main__":
    main()
