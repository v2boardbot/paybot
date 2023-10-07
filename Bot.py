from telegram.ext import CommandHandler, Application, ContextTypes
from commands import info, cash_out, on, off, money
import os
from datetime import datetime, time
from Pay import pay
from utils import read_config
import pytz

config = read_config()
print('配置:', config, '\n')
bot_config = config.get('bot')
proxy = bot_config.get('proxy')
if proxy:
    print('设置代理地址:', proxy)
    os.environ['HTTP_PROXY'] = proxy
    os.environ['HTTPS_PROXY'] = proxy

CommandList = [
    CommandHandler("info", info),
    CommandHandler("money", money),
    CommandHandler("cash_out", cash_out),
    CommandHandler("on", on),
    CommandHandler("off", off),
]


async def set_commands(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.set_my_commands(commands=[
        ("money", "查看余额"),
        ("info", "查看收入详细"),
        ("cash_out", "提现"),
        ("on", "开启自动提现"),
        ("off", "关闭自动提现"),
    ])


async def auto_cash_out(context: ContextTypes.DEFAULT_TYPE):
    if config.get('pay').get('auto') == 'on':
        await context.bot.send_message(chat_id=bot_config.get('chat_id'), text=f'提现结果: {pay.cash_out()}')


if __name__ == '__main__':
    application = Application.builder().token(bot_config.get('token')).build()
    job_queue = application.job_queue
    job_queue.run_once(set_commands, 2)
    ctc_time = datetime.strptime(config.get('pay').get('time'), "%H:%M:%S").time()
    run_time = time(hour=ctc_time.hour, minute=ctc_time.minute, second=ctc_time.second, tzinfo=pytz.timezone('Asia/Shanghai'))
    print('自动提现时间:', run_time)
    print('自动提现开关:', config.get('pay').get('auto') == 'on')
    job_queue.run_daily(callback=auto_cash_out, time=run_time)
    for handler in CommandList:
        application.add_handler(handler)
    print('启动')
    application.run_polling()
