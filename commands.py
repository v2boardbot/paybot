from telegram import Update
from telegram.ext import ContextTypes
from Pay import pay
from utils import read_config, save_config
from datetime import datetime


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = pay.query_info()
    text = ''
    if isinstance(data, dict):
        for k, v in data.items():
            text += f'{k}: {v}\n'
    else:
        text = data
    await update.message.reply_text(text=text)

async def money(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = pay.query_money()
    text = ''
    if isinstance(data, dict):
        for k, v in data.items():
            text += f'{k}: {v}\n'
    else:
        text = data
    await update.message.reply_text(text=text)

async def cash_out(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text=f'提现结果: {pay.cash_out()}')


async def on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    config = read_config()
    run_time = datetime.strptime(config.get('pay').get('time'), "%H:%M:%S").time()
    config['pay']['auto'] = 'on'
    save_config(config)
    await update.message.reply_text(text=f'开启自动提现成功，自动提现时间：{run_time}')


async def off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    config = read_config()
    config['pay']['auto'] = 'off'
    save_config(config)
    await update.message.reply_text(text=f'关闭自动提现成功')
