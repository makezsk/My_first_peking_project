# 作者 宗圣凯 时间 2026-04-02
import time
import tkinter as tk
from tkinter import scrolledtext, messagebox
import pymysql
from cozepy import COZE_CN_BASE_URL, Coze, TokenAuth, Message, ChatStatus

# =========================
# 1. MySQL 配置
# =========================
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "admin"
DB_NAME = "diet_system"

# =========================
# 2. Coze 配置
# =========================
COZE_API_TOKEN = "cztei_hw7rfJru7oN6O3quleSZoJRV64qZEctZJ3sgAKG4TzuvOgenUUDTCyYlhetG6Ec1U"   # token
BOT_ID = "7624056708306370560"  # bot_id
USER_ID = "user_001"

# 初始化 Coze 客户端
coze = Coze(
    auth=TokenAuth(token=COZE_API_TOKEN),
    base_url=COZE_CN_BASE_URL
)

# 当前登录用户名
current_username = None


# =========================
# 3. 数据库连接函数
# =========================
def get_conn():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset="utf8mb4"
    )


# =========================
# 4. 注册函数
# =========================
def register_user(username, password):
    try:
        conn = get_conn()
        cursor = conn.cursor()

        sql = "INSERT INTO sys_user (username, password) VALUES (%s, %s)"
        cursor.execute(sql, (username, password))
        conn.commit()

        cursor.close()
        conn.close()
        return True, "注册成功"

    except Exception as e:
        return False, f"注册失败：{e}"


# =========================
# 5. 登录函数
# =========================
def login_user(username, password):
    try:
        conn = get_conn()
        cursor = conn.cursor()

        sql = "SELECT * FROM sys_user WHERE username=%s AND password=%s"
        cursor.execute(sql, (username, password))
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result:
            return True, "登录成功"
        else:
            return False, "账号或密码错误"

    except Exception as e:
        return False, f"登录失败：{e}"


# =========================
# 6. 提取 assistant 回复
# =========================
def extract_assistant_messages(messages):
    answers = []

    for msg in messages:
        role = getattr(msg, "role", None)
        content = getattr(msg, "content", "")

        if role == "assistant" and content:
            answers.append(str(content).strip())

    return answers


# =========================
# 7. Coze 非流式提问
# 超时时间 200 秒
# =========================
def ask_bot_no_stream(question, timeout=200, poll_interval=1):
    try:
        chat = coze.chat.create(
            bot_id=BOT_ID,
            user_id=USER_ID,
            additional_messages=[
                Message.build_user_question_text(question),
            ],
        )

        chat_id = chat.id
        conversation_id = chat.conversation_id

        start_time = time.time()

        while True:
            chat_detail = coze.chat.retrieve(
                conversation_id=conversation_id,
                chat_id=chat_id
            )

            status = chat_detail.status

            if status == ChatStatus.COMPLETED:
                break

            if status in [ChatStatus.FAILED, ChatStatus.CANCELED]:
                return f"对话失败，状态：{status}"

            if time.time() - start_time > timeout:
                return "对话超时，请稍后重试。"

            time.sleep(poll_interval)

        messages = coze.chat.messages.list(
            conversation_id=conversation_id,
            chat_id=chat_id
        )

        answer_list = extract_assistant_messages(messages)

        if not answer_list:
            return "未获取到有效回复。"

        final_answer = "\n".join(answer_list).strip()
        return final_answer

    except Exception as e:
        return f"调用接口时发生异常：{e}"


# =========================
# 8. 打开问答窗口
# =========================
def open_chat_window():
    chat_root = tk.Tk()
    chat_root.title("中医食疗问答系统")
    chat_root.geometry("800x600")

    title_label = tk.Label(
        chat_root,
        text=f"中医食疗问答系统 - 当前用户：{current_username}",
        font=("微软雅黑", 16)
    )
    title_label.pack(pady=10)

    entry = tk.Entry(chat_root, font=("微软雅黑", 12), width=60)
    entry.pack(pady=10)

    def send_question():
        question = entry.get().strip()

        if not question:
            messagebox.showwarning("提示", "请输入问题")
            return

        output_text.insert(tk.END, "你：" + question + "\n")
        output_text.insert(tk.END, "AI：正在思考，请稍候...\n")
        output_text.update()

        answer = ask_bot_no_stream(question)

        output_text.delete("end-2l", "end-1l")
        output_text.insert(tk.END, "AI：" + answer + "\n")
        output_text.insert(tk.END, "-" * 60 + "\n")

        entry.delete(0, tk.END)

    # 先放按钮
    send_button = tk.Button(
        chat_root,
        text="发送问题",
        font=("微软雅黑", 12),
        width=12,
        command=send_question
    )
    send_button.pack(pady=5)

    # 再放输出框
    output_text = scrolledtext.ScrolledText(
        chat_root,
        wrap=tk.WORD,
        font=("微软雅黑", 12),
        width=90,
        height=25
    )
    output_text.pack(pady=10)

    chat_root.mainloop()


# =========================
# 9. 登录窗口逻辑
# =========================
def open_login_window():
    login_root = tk.Tk()
    login_root.title("登录/注册")
    login_root.geometry("400x280")

    tk.Label(login_root, text="中医食疗问答系统", font=("微软雅黑", 16)).pack(pady=15)

    tk.Label(login_root, text="账号：", font=("微软雅黑", 12)).pack()
    username_entry = tk.Entry(login_root, font=("微软雅黑", 12), width=25)
    username_entry.pack(pady=5)

    tk.Label(login_root, text="密码：", font=("微软雅黑", 12)).pack()
    password_entry = tk.Entry(login_root, font=("微软雅黑", 12), width=25, show="*")
    password_entry.pack(pady=5)

    def do_register():
        username = username_entry.get().strip()
        password = password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("提示", "请输入账号和密码")
            return

        ok, msg = register_user(username, password)
        if ok:
            messagebox.showinfo("提示", msg)
        else:
            messagebox.showerror("提示", msg)

    def do_login():
        global current_username

        username = username_entry.get().strip()
        password = password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("提示", "请输入账号和密码")
            return

        ok, msg = login_user(username, password)
        if ok:
            current_username = username
            messagebox.showinfo("提示", msg)
            login_root.destroy()
            open_chat_window()
        else:
            messagebox.showerror("提示", msg)

    btn_frame = tk.Frame(login_root)
    btn_frame.pack(pady=20)

    login_btn = tk.Button(btn_frame, text="登录", font=("微软雅黑", 12), width=10, command=do_login)
    login_btn.grid(row=0, column=0, padx=10)

    register_btn = tk.Button(btn_frame, text="注册", font=("微软雅黑", 12), width=10, command=do_register)
    register_btn.grid(row=0, column=1, padx=10)

    login_root.mainloop()


# =========================
# 10. 程序入口
# =========================
if __name__ == "__main__":
    open_login_window()