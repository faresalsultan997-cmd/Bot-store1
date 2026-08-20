import discord
from discord.ext import commands
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import os
import asyncio
import re


# =========================================================
# ⚙️ إعدادات المتجر
# =========================================================

OWNER_ID = 1531438534244700313

PROBOT_ID = 282859044593598464

PREFIX = "!"

PAYMENT_TIMEOUT = 15 * 60

# ضريبة ProBot
PROBOT_TAX_RATE = 0.05


# =========================================================
# 💰 حساب مبلغ التحويل مع الضريبة
# =========================================================

def calculate_transfer_amount(price):
    """
    يحسب المبلغ الذي يجب على العميل تحويله
    حتى يستلم صاحب المتجر السعر الأساسي بعد خصم الضريبة.
    """

    return int(
        (price / (1 - PROBOT_TAX_RATE)) + 0.999999
    )


# =========================================================
# 🤖 إعداد البوت
# =========================================================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix=PREFIX,
    intents=intents,
    help_command=None
)


# =========================================================
# 🛒 المنتجات
# =========================================================

PRODUCTS = {

    # =====================================================
    # 👤 اليوزرات
    # =====================================================

    "username_5": {
        "name": "يوزر خماسي",
        "price": 100_000,
        "category": "يوزرات"
    },

    "username_4": {
        "name": "يوزر رباعي",
        "price": 175_000,
        "category": "يوزرات"
    },

    "username_3": {
        "name": "يوزر ثلاثي",
        "price": 250_000,
        "category": "يوزرات"
    },

    "username_2": {
        "name": "يوزر ثنائي",
        "price": 360_000,
        "category": "يوزرات"
    },

    # =====================================================
    # 🛠️ الأدوات
    # =====================================================

    "snowfox": {
        "name": "🦊 أداة Snow Fox",
        "price": 3_000_000,
        "category": "أدوات"
    },

    "limited_users": {
        "name": "👤 أداة يوزرات محدودة",
        "price": 2_500_000,
        "category": "أدوات"
    },

    "server_copy": {
        "name": "📋 أداة نسخ سيرفرات",
        "price": 3_000_000,
        "category": "أدوات"
    },

    # =====================================================
    # 🤖 شراء بوتات
    # =====================================================

    "buy_ticket_bot": {
        "name": "🎫 بوت تذاكر",
        "price": 1_500_000,
        "category": "شراء_بوتات"
    },

    "buy_chat_bot": {
        "name": "💬 بوت دردشة",
        "price": 1_200_000,
        "category": "شراء_بوتات"
    },

    "buy_rooms_bot": {
        "name": "🏠 بوت رومات",
        "price": 1_400_000,
        "category": "شراء_بوتات"
    },

    "buy_system_bot": {
        "name": "⚙️ بوت سيستم",
        "price": 3_000_000,
        "category": "شراء_بوتات"
    },

    "buy_store_bot": {
        "name": "🛒 بوت متجر",
        "price": 2_500_000,
        "category": "شراء_بوتات"
    },

    # =====================================================
    # 🛠️ صناعة بوتات
    # =====================================================

    "make_ticket_bot": {
        "name": "🎫 صناعة بوت تذاكر",
        "price": 3_000_000,
        "category": "صناعة_بوتات"
    },

    "make_chat_bot": {
        "name": "💬 صناعة بوت دردشة",
        "price": 2_700_000,
        "category": "صناعة_بوتات"
    },

    "make_rooms_bot": {
        "name": "🏠 صناعة بوت رومات",
        "price": 2_900_000,
        "category": "صناعة_بوتات"
    },

    "make_system_bot": {
        "name": "⚙️ صناعة بوت سيستم",
        "price": 6_000_000,
        "category": "صناعة_بوتات"
    },

    "make_store_bot": {
        "name": "🛒 صناعة بوت متجر",
        "price": 5_500_000,
        "category": "صناعة_بوتات"
    }
}


USERNAME_PRODUCTS = {
    "username_5",
    "username_4",
    "username_3",
    "username_2"
}


BOT_PRODUCTS = {
    "buy_ticket_bot",
    "buy_chat_bot",
    "buy_rooms_bot",
    "buy_system_bot",
    "buy_store_bot",
    "make_ticket_bot",
    "make_chat_bot",
    "make_rooms_bot",
    "make_system_bot",
    "make_store_bot"
}


# =========================================================
# 👤 مخزون اليوزرات
# =========================================================

USERNAME_STOCK = {

    "username_5": [
        "ftzvx",
        "rrbh9",
        "typns",
        "11ml5",
        "pk5jd",
        "0pyey",
        "wd4kl",
        "j9yya",
        "vvc1i",
        "sesmy",
        "7q86t",
        "1ee3t",
        "oumg0",
        "q3ryx",
        "bisfn",
        "ffnpn",
        "ty96m",
        "37au3",
        "vv5nj",
        "l9wht",
        "vbtcr",
        "m3953",
        "39ser",
        "09mwz",
        "cey0u",
        "hkae4",
        "2tyqd",
        "hs6sf",
        "5f4tw",
        "jg1lt",
        "687k1",
        "74s4h",
        "18i5k",
        "88znk",
        "j961f",
        "i98ra",
        "2tuao",
        "adejf",
        "v84i6",
        "wzn3f",
        "904ez",
        "2ypuk",
        "kx6xd",
        "1ckxz",
        "txftx",
        "prug3",
        "3erf7",
        "dtbwz",
        "suf30",
        "mnjc7"
    ],

    "username_4": [
        "qu7m",
        "wg6y",
        "9lan",
        "dg1h",
        "d6qg",
        "e7ba",
        "gopj",
        "webm",
        "0jd4",
        "7ipj",
        "yee0",
        "18lk",
        "h98k",
        "0v1x",
        "69pt",
        "afs3",
        "ywnt",
        "siyr",
        "iu3s",
        "x23b",
        "r5e9",
        "lzub",
        "jlkl",
        "6zxj",
        "onv5",
        "9f5m",
        "nm4o",
        "bov8",
        "mirx",
        "gtr5",
        "31jy",
        "k0ut",
        "urmp",
        "4k6n",
        "b5ii",
        "43or",
        "szxc",
        "nqt7",
        "tlc0",
        "5uhq",
        "brj2",
        "fnbn",
        "d47l"
    ],

    "username_3": [
        "u96",
        "8kl",
        "h5u",
        "cgf",
        "q62",
        "pzl",
        "p07",
        "fpg",
        "nej",
        "2kb",
        "ooq",
        "9g4",
        "ir8",
        "9de",
        "b8o",
        "rcn",
        "779",
        "jl7",
        "may",
        "4rn",
        "h10",
        "0cj",
        "5yc",
        "kqu",
        "kbr",
        "yoo",
        "sn4",
        "6ha",
        "xh7",
        "s24",
        "t3z",
        "851",
        "ngt",
        "pcf",
        "20c",
        "atk",
        "cr6",
        "8x0",
        "m3a",
        "0fy",
        "zoe",
        "et4",
        "c3v",
        "73g",
        "mf9",
        "d0s",
        "dya",
        "2tx",
        "9qz"
    ],

    "username_2": [
        "3o",
        "db",
        "yn",
        "hs",
        "fl",
        "pk",
        "yq",
        "ec",
        "fn",
        "06",
        "q3",
        "h0",
        "w0",
        "z1",
        "ti",
        "4b",
        "nd",
        "0y",
        "d9",
        "j5",
        "1s",
        "y4",
        "lb",
        "vx",
        "ry",
        "l5",
        "x2",
        "3w",
        "fx",
        "6h",
        "1v",
        "4y",
        "yo",
        "kl",
        "4z",
        "et",
        "kb",
        "3h",
        "z7",
        "st",
        "2q"
    ]
}


# =========================================================
# 🗄️ PostgreSQL
# =========================================================

DATABASE_URL = (
    os.getenv("DATABASE_URL")
    or os.getenv("DATABASE_PRIVATE_URL")
    or os.getenv("DATABASE_PUBLIC_URL")
)

if not DATABASE_URL:

    pg_host = os.getenv("PGHOST")
    pg_port = os.getenv("PGPORT", "5432")
    pg_database = os.getenv("PGDATABASE")
    pg_user = os.getenv("PGUSER")
    pg_password = os.getenv("PGPASSWORD")

    if all([
        pg_host,
        pg_port,
        pg_database,
        pg_user,
        pg_password
    ]):

        DATABASE_URL = (
            f"postgresql://{pg_user}:{pg_password}"
            f"@{pg_host}:{pg_port}/{pg_database}"
        )


if not DATABASE_URL:

    raise RuntimeError(
        "❌ لم يتم العثور على DATABASE_URL أو بيانات PostgreSQL."
    )


db = psycopg2.connect(DATABASE_URL)
db.autocommit = False

cursor = db.cursor(
    cursor_factory=RealDictCursor
)


# =========================================================
# 🧱 الجداول
# =========================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    product_id TEXT NOT NULL,
    product_name TEXT NOT NULL,
    price BIGINT NOT NULL,
    delivered_product TEXT,
    created_at TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS username_stock (
    id SERIAL PRIMARY KEY,
    product_id TEXT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    sold INTEGER NOT NULL DEFAULT 0
)
""")

db.commit()


# =========================================================
# 📥 تحميل الستوك
# =========================================================

def initialize_username_stock():

    for product_id, usernames in USERNAME_STOCK.items():

        for username in usernames:

            cursor.execute(
                """
                INSERT INTO username_stock
                (
                    product_id,
                    username,
                    sold
                )
                VALUES (%s, %s, 0)
                ON CONFLICT (username) DO NOTHING
                """,
                (
                    product_id,
                    username
                )
            )

    db.commit()


initialize_username_stock()


# =========================================================
# 🔒 قفل عمليات الشراء
# =========================================================

purchase_lock = asyncio.Lock()


# =========================================================
# 👤 جلسات المستخدمين
# =========================================================

verified_users = set()


# =========================================================
# 💳 عمليات الدفع الحالية
# =========================================================

pending_payments = {}


# =========================================================
# 🔤 تنظيف الاسم للمطابقة
# =========================================================

def normalize_name(value):

    if not value:
        return ""

    value = str(value)

    value = value.strip()
    value = value.lower()

    value = value.replace("@", "")
    value = value.replace(" ", "")

    return value


def get_user_name_variants(user):

    variants = set()

    variants.add(
        normalize_name(user.name)
    )

    variants.add(
        normalize_name(user.display_name)
    )

    if user.global_name:

        variants.add(
            normalize_name(user.global_name)
        )

    return {
        value
        for value in variants
        if value
    }


# =========================================================
# 💳 قراءة رسالة ProBot
# =========================================================

def extract_probot_transfer(message):

    if message.author.id != PROBOT_ID:
        return None

    text_parts = []

    if message.content:
        text_parts.append(
            message.content
        )

    for embed in message.embeds:

        if embed.title:
            text_parts.append(
                embed.title
            )

        if embed.description:
            text_parts.append(
                embed.description
            )

        for field in embed.fields:

            if field.name:
                text_parts.append(
                    field.name
                )

            if field.value:
                text_parts.append(
                    field.value
                )

    text = "\n".join(text_parts)

    pattern = re.compile(
        r"(.+?)"
        r"\s*(?:has\s+transferred|transferred)"
        r"\s*[`$]*([\d,]+(?:\.\d+)?)"
        r"[`$]*"
        r"\s*to\s*<@!?(\d+)>",
        re.IGNORECASE
    )

    match = pattern.search(text)

    if not match:
        return None

    sender_name = match.group(1).strip()

    amount_text = (
        match.group(2)
        .replace(",", "")
    )

    receiver_id = int(
        match.group(3)
    )

    try:

        amount = int(
            float(amount_text)
        )

    except ValueError:

        return None

    return {
        "sender_name": sender_name,
        "amount": amount,
        "receiver_id": receiver_id,
        "message_id": message.id
    }


# =========================================================
# 💳 انتظار التحويل
# =========================================================

async def wait_for_payment(
    interaction,
    product
):

    buyer = interaction.user

    buyer_id = buyer.id

    channel_id = interaction.channel.id

    # السعر الأصلي
    base_price = product["price"]

    # السعر شامل الضريبة
    amount = calculate_transfer_amount(
        base_price
    )

    payment_key = (
        f"{buyer_id}-"
        f"{interaction.id}"
    )

    pending_payments[payment_key] = {
        "user_id": buyer_id,
        "amount": amount,
        "base_price": base_price,
        "product_id": None,
        "channel_id": channel_id,
        "started_at": datetime.now()
    }

    name_variants = get_user_name_variants(
        buyer
    )

    transfer_command = (
        f"C @{OWNER_ID} {amount}"
    )

    tax_amount = amount - base_price

    await interaction.channel.send(
        content=buyer.mention,
        embed=discord.Embed(
            title="💳 بانتظار التحويل",
            description=(
                f"📦 المنتج: **{product['name']}**\n\n"

                f"💰 السعر الأساسي: "
                f"`{base_price:,}` كريدت\n"

                f"🧾 ضريبة ProBot (5%): "
                f"`{tax_amount:,}` كريدت\n\n"

                f"💳 **المبلغ المطلوب تحويله: "
                f"`{amount:,}` كريدت**\n\n"

                "📤 قم بالتحويل بالأمر:\n"
                f"```{transfer_command}```\n\n"

                "⏱️ لديك **15 دقيقة** لإتمام التحويل.\n\n"

                "⚠️ سيتم التحقق من رسالة ProBot الحقيقية."
            ),
            color=0xF1C40F
        )
    )

    def check(message):

        # -------------------------------------------------
        # لازم تكون الرسالة من ProBot
        # -------------------------------------------------

        if message.author.id != PROBOT_ID:
            return False

        # -------------------------------------------------
        # نفس الروم
        # -------------------------------------------------

        if message.channel.id != channel_id:
            return False

        transfer = extract_probot_transfer(
            message
        )

        if not transfer:
            return False

        # -------------------------------------------------
        # المستلم
        # -------------------------------------------------

        if transfer["receiver_id"] != OWNER_ID:
            return False

        # -------------------------------------------------
        # المبلغ شامل الضريبة
        # -------------------------------------------------

        if transfer["amount"] != amount:
            return False

        # -------------------------------------------------
        # صاحب التحويل
        # -------------------------------------------------

        sender_name = normalize_name(
            transfer["sender_name"]
        )

        sender_name = sender_name.rstrip(
            ".,:"
        )

        cleaned_variants = set()

        for name in name_variants:

            cleaned = name.rstrip(
                ".,:"
            )

            cleaned_variants.add(
                cleaned
            )

        if sender_name not in cleaned_variants:
            return False

        return True

    try:

        message = await bot.wait_for(
            "message",
            timeout=PAYMENT_TIMEOUT,
            check=check
        )

    except asyncio.TimeoutError:

        pending_payments.pop(
            payment_key,
            None
        )

        await interaction.channel.send(
            embed=discord.Embed(
                title="⏰ انتهى وقت التحويل",
                description=(
                    f"{buyer.mention}\n\n"
                    "انتهت مدة **15 دقيقة** "
                    "ولم يتم العثور على تحويل صحيح.\n\n"
                    "الرجاء بدء عملية شراء جديدة."
                ),
                color=0xE74C3C
            )
        )

        return False

    transfer = extract_probot_transfer(
        message
    )

    pending_payments.pop(
        payment_key,
        None
    )

    if not transfer:
        return False

    # تحقق نهائي
    if transfer["receiver_id"] != OWNER_ID:
        return False

    if transfer["amount"] != amount:
        return False

    sender_name = normalize_name(
        transfer["sender_name"]
    ).rstrip(".,:")

    if sender_name not in {
        n.rstrip(".,:")
        for n in name_variants
    }:

        return False

    return True


# =========================================================
# 📦 سحب يوزر من الستوك
# =========================================================

def reserve_username(product_id):

    cursor.execute(
        """
        SELECT id, username
        FROM username_stock
        WHERE product_id = %s
        AND sold = 0
        ORDER BY id ASC
        LIMIT 1
        """,
        (product_id,)
    )

    row = cursor.fetchone()

    if row is None:
        return None

    cursor.execute(
        """
        UPDATE username_stock
        SET sold = 1
        WHERE id = %s
        AND sold = 0
        """,
        (row["id"],)
    )

    if cursor.rowcount == 0:

        db.rollback()

        return None

    db.commit()

    return row["username"]


# =========================================================
# 📊 عدد الستوك
# =========================================================

def get_stock_count(product_id):

    cursor.execute(
        """
        SELECT COUNT(*) AS count
        FROM username_stock
        WHERE product_id = %s
        AND sold = 0
        """,
        (product_id,)
    )

    result = cursor.fetchone()

    return result["count"]


# =========================================================
# 🔄 إرجاع يوزر
# =========================================================

def return_username(
    product_id,
    username
):

    cursor.execute(
        """
        UPDATE username_stock
        SET sold = 0
        WHERE product_id = %s
        AND username = %s
        """,
        (
            product_id,
            username
        )
    )

    db.commit()


# =========================================================
# 🔀 احتمالات اليوزر
# =========================================================

def generate_username_variants(username):

    variants = set()

    variants.add(username)

    for i in range(
        1,
        len(username)
    ):

        variants.add(
            username[:i]
            + "."
            + username[i:]
        )

        variants.add(
            username[:i]
            + "_"
            + username[i:]
        )

    if len(username) >= 3:

        for i in range(
            1,
            len(username)
        ):

            for j in range(
                i + 1,
                len(username)
            ):

                variants.add(
                    username[:i]
                    + "."
                    + username[i:j]
                    + "."
                    + username[j:]
                )

                variants.add(
                    username[:i]
                    + "_"
                    + username[i:j]
                    + "_"
                    + username[j:]
                )

    return list(variants)


# =========================================================
# 🏠 Embed المتجر
# =========================================================

def main_embed():

    embed = discord.Embed(
        title="🛒 متجر الخدمات",
        description=(
            "مرحبًا بك في متجرنا ❤️\n\n"
            "اختر القسم الذي تريد الدخول إليه:"
        ),
        color=0x2ECC71,
        timestamp=datetime.now()
    )

    embed.add_field(
        name="👤 اليوزرات",
        value="خماسي • رباعي • ثلاثي • ثنائي",
        inline=False
    )

    embed.add_field(
        name="🛠️ الأدوات",
        value=(
            "Snow Fox • يوزرات محدودة • نسخ سيرفرات"
        ),
        inline=False
    )

    embed.add_field(
        name="🤖 البوتات",
        value=(
            "شراء بوتات • صناعة بوتات"
        ),
        inline=False
    )

    embed.add_field(
        name="💳 الدفع",
        value="الدفع يتم عن طريق ProBot.",
        inline=False
    )

    embed.add_field(
        name="📝 طلب آخر",
        value=(
            f"للطلبات الأخرى تواصل مع <@{OWNER_ID}>."
        ),
        inline=False
    )

    embed.set_footer(
        text="متجر الخدمات • الدفع عبر ProBot"
    )

    return embed


# =========================================================
# 🏠 القائمة الرئيسية
# =========================================================

class MainMenuView(discord.ui.View):

    def __init__(
        self,
        user_id
    ):

        super().__init__(
            timeout=300
        )

        self.user_id = user_id

    async def interaction_check(
        self,
        interaction
    ):

        if interaction.user.id != self.user_id:

            await interaction.response.send_message(
                "❌ هذه القائمة ليست لك.",
                ephemeral=True
            )

            return False

        return True

    @discord.ui.button(
        label="شراء يوزرات",
        emoji="👤",
        style=discord.ButtonStyle.primary
    )
    async def usernames(
        self,
        interaction,
        button
    ):

        embed = discord.Embed(
            title="👤 شراء يوزرات",
            description=(
                "اختر نوع اليوزر الذي تريده:"
            ),
            color=0x3498DB
        )

        await interaction.response.edit_message(
            embed=embed,
            view=ProductsView(
                "يوزرات",
                self.user_id
            )
        )

    @discord.ui.button(
        label="شراء أدوات",
        emoji="🛠️",
        style=discord.ButtonStyle.success
    )
    async def tools(
        self,
        interaction,
        button
    ):

        embed = discord.Embed(
            title="🛠️ شراء أدوات",
            description=(
                "اختر الأداة التي تريد شراءها:"
            ),
            color=0x9B59B6
        )

        await interaction.response.edit_message(
            embed=embed,
            view=ProductsView(
                "أدوات",
                self.user_id
            )
        )

    @discord.ui.button(
        label="البوتات",
        emoji="🤖",
        style=discord.ButtonStyle.primary,
        row=1
    )
    async def bots(
        self,
        interaction,
        button
    ):

        embed = discord.Embed(
            title="🤖 قسم البوتات",
            description=(
                "اختر الخدمة التي تريدها:\n\n"
                "🛒 شراء بوت جاهز\n"
                "🛠️ صناعة بوت خاص"
            ),
            color=0x5865F2
        )

        await interaction.response.edit_message(
            embed=embed,
            view=BotsCategoryView(
                self.user_id
            )
        )

    @discord.ui.button(
        label="طلب آخر",
        emoji="📝",
        style=discord.ButtonStyle.secondary,
        row=2
    )
    async def other(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            embed=discord.Embed(
                title="📝 طلب آخر",
                description=(
                    f"للطلبات الأخرى تواصل مع "
                    f"<@{OWNER_ID}>."
                ),
                color=0xF1C40F
            ),
            view=OtherRequestView(
                self.user_id
            )
        )


# =========================================================
# 📝 طلب آخر
# =========================================================

class OtherRequestView(
    discord.ui.View
):

    def __init__(
        self,
        user_id
    ):

        super().__init__(
            timeout=300
        )

        self.user_id = user_id

    async def interaction_check(
        self,
        interaction
    ):

        return interaction.user.id == self.user_id

    @discord.ui.button(
        label="رجوع",
        emoji="⬅️",
        style=discord.ButtonStyle.secondary
    )
    async def back(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            embed=main_embed(),
            view=MainMenuView(
                self.user_id
            )
        )


# =========================================================
# 🤖 قسم البوتات
# =========================================================

class BotsCategoryView(
    discord.ui.View
):

    def __init__(
        self,
        user_id
    ):

        super().__init__(
            timeout=300
        )

        self.user_id = user_id

    async def interaction_check(
        self,
        interaction
    ):

        if interaction.user.id != self.user_id:

            await interaction.response.send_message(
                "❌ هذه القائمة ليست لك.",
                ephemeral=True
            )

            return False

        return True

    @discord.ui.button(
        label="شراء بوت",
        emoji="🛒",
        style=discord.ButtonStyle.success
    )
    async def buy(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            embed=discord.Embed(
                title="🛒 شراء بوتات",
                description="اختر البوت الذي تريد شراءه:",
                color=0x2ECC71
            ),
            view=BotProductsView(
                "شراء_بوتات",
                self.user_id
            )
        )

    @discord.ui.button(
        label="صناعة بوت",
        emoji="🛠️",
        style=discord.ButtonStyle.primary
    )
    async def make(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            embed=discord.Embed(
                title="🛠️ صناعة بوتات",
                description=(
                    "اختر نوع البوت الذي تريد صناعته:"
                ),
                color=0x9B59B6
            ),
            view=BotProductsView(
                "صناعة_بوتات",
                self.user_id
            )
        )

    @discord.ui.button(
        label="رجوع",
        emoji="⬅️",
        style=discord.ButtonStyle.secondary,
        row=2
    )
    async def back(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            embed=main_embed(),
            view=MainMenuView(
                self.user_id
            )
        )


# =========================================================
# 🤖 منتجات البوتات
# =========================================================

class BotProductsView(
    discord.ui.View
):

    def __init__(
        self,
        category,
        user_id
    ):

        super().__init__(
            timeout=300
        )

        self.user_id = user_id

        products = [
            (pid, product)
            for pid, product in PRODUCTS.items()
            if product["category"] == category
        ]

        for product_id, product in products:

            button = discord.ui.Button(
                label=(
                    f"{product['name']} • "
                    f"{product['price']:,}"
                )[:80],
                style=discord.ButtonStyle.primary
            )

            async def callback(
                interaction,
                pid=product_id
            ):

                if interaction.user.id != self.user_id:

                    await interaction.response.send_message(
                        "❌ هذه القائمة ليست لك.",
                        ephemeral=True
                    )

                    return

                product_data = PRODUCTS.get(pid)

                if not product_data:

                    await interaction.response.send_message(
                        "❌ المنتج غير موجود.",
                        ephemeral=True
                    )

                    return

                price = product_data["price"]
                transfer_amount = calculate_transfer_amount(
                    price
                )

                tax_amount = (
                    transfer_amount - price
                )

                embed = discord.Embed(
                    title="🛒 تأكيد الطلب",
                    description=(
                        "راجع بيانات الطلب قبل الدفع:"
                    ),
                    color=0x3498DB
                )

                embed.add_field(
                    name="📦 المنتج",
                    value=product_data["name"],
                    inline=False
                )

                embed.add_field(
                    name="💰 السعر الأساسي",
                    value=(
                        f"`{price:,}` كريدت"
                    ),
                    inline=False
                )

                embed.add_field(
                    name="🧾 ضريبة ProBot",
                    value=(
                        f"`{tax_amount:,}` كريدت"
                    ),
                    inline=False
                )

                embed.add_field(
                    name="💳 المبلغ المطلوب تحويله",
                    value=(
                        f"`{transfer_amount:,}` كريدت"
                    ),
                    inline=False
                )

                await interaction.response.edit_message(
                    embed=embed,
                    view=ConfirmView(
                        pid,
                        self.user_id
                    )
                )

            button.callback = callback

            self.add_item(button)

        back = discord.ui.Button(
            label="رجوع",
            emoji="⬅️",
            style=discord.ButtonStyle.secondary,
            row=4
        )

        async def back_callback(
            interaction
        ):

            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="🤖 قسم البوتات",
                    description=(
                        "اختر الخدمة التي تريدها:\n\n"
                        "🛒 شراء بوت جاهز\n"
                        "🛠️ صناعة بوت خاص"
                    ),
                    color=0x5865F2
                ),
                view=BotsCategoryView(
                    self.user_id
                )
            )

        back.callback = back_callback

        self.add_item(back)


# =========================================================
# 📦 منتجات اليوزرات والأدوات
# =========================================================

class ProductsView(
    discord.ui.View
):

    def __init__(
        self,
        category,
        user_id
    ):

        super().__init__(
            timeout=300
        )

        self.category = category
        self.user_id = user_id

        products = [
            (pid, product)
            for pid, product in PRODUCTS.items()
            if product["category"] == category
        ]

        for product_id, product in products:

            label = (
                f"{product['name']} • "
                f"{product['price']:,}"
            )

            if product_id in USERNAME_PRODUCTS:

                label += (
                    f" • متوفر: "
                    f"{get_stock_count(product_id)}"
                )

            button = discord.ui.Button(
                label=label[:80],
                style=discord.ButtonStyle.primary
            )

            async def callback(
                interaction,
                pid=product_id
            ):

                if interaction.user.id != self.user_id:

                    await interaction.response.send_message(
                        "❌ هذه القائمة ليست لك.",
                        ephemeral=True
                    )

                    return

                product_data = PRODUCTS.get(pid)

                if not product_data:

                    await interaction.response.send_message(
                        "❌ المنتج غير موجود.",
                        ephemeral=True
                    )

                    return

                if pid in USERNAME_PRODUCTS:

                    if get_stock_count(pid) <= 0:

                        await interaction.response.send_message(
                            "❌ عذرًا، هذا النوع من اليوزرات نفد.",
                            ephemeral=True
                        )

                        return

                price = product_data["price"]
                transfer_amount = calculate_transfer_amount(
                    price
                )

                tax_amount = (
                    transfer_amount - price
                )

                embed = discord.Embed(
                    title="🛒 تأكيد الطلب",
                    description=(
                        "راجع بيانات الطلب قبل الدفع:"
                    ),
                    color=0x3498DB
                )

                embed.add_field(
                    name="📦 المنتج",
                    value=product_data["name"],
                    inline=False
                )

                embed.add_field(
                    name="💰 السعر الأساسي",
                    value=(
                        f"`{price:,}` كريدت"
                    ),
                    inline=False
                )

                embed.add_field(
                    name="🧾 ضريبة ProBot",
                    value=(
                        f"`{tax_amount:,}` كريدت"
                    ),
                    inline=False
                )

                embed.add_field(
                    name="💳 المبلغ المطلوب تحويله",
                    value=(
                        f"`{transfer_amount:,}` كريدت"
                    ),
                    inline=False
                )

                await interaction.response.edit_message(
                    embed=embed,
                    view=ConfirmView(
                        pid,
                        self.user_id
                    )
                )

            button.callback = callback

            self.add_item(button)

        back = discord.ui.Button(
            label="رجوع",
            emoji="⬅️",
            style=discord.ButtonStyle.secondary,
            row=4
        )

        async def back_callback(
            interaction
        ):

            await interaction.response.edit_message(
                embed=main_embed(),
                view=MainMenuView(
                    self.user_id
                )
            )

        back.callback = back_callback

        self.add_item(back)


# =========================================================
# 📸 طلب دليل الشراء
# =========================================================

async def request_purchase_proof(
    interaction,
    product
):

    channel = interaction.channel
    buyer = interaction.user

    await channel.send(
        content=buyer.mention,
        embed=discord.Embed(
            title="📸 دليل الشراء",
            description=(
                f"تم التحقق من تحويلك بنجاح ✅\n\n"
                f"📦 المنتج: **{product['name']}**\n\n"
                "الرجاء التواصل مع صاحب المتجر:\n"
                f"<@{OWNER_ID}>\n\n"
                "وأرسل له **صورة دليل الشراء**."
            ),
            color=0x2ECC71
        )
    )


# =========================================================
# ✅ تأكيد الطلب
# =========================================================

class ConfirmView(
    discord.ui.View
):

    def __init__(
        self,
        product_id,
        buyer_id
    ):

        super().__init__(
            timeout=120
        )

        self.product_id = product_id
        self.buyer_id = buyer_id

    async def interaction_check(
        self,
        interaction
    ):

        if interaction.user.id != self.buyer_id:

            await interaction.response.send_message(
                "❌ هذه العملية ليست لك.",
                ephemeral=True
            )

            return False

        return True

    @discord.ui.button(
        label="الدفع الآن",
        emoji="💳",
        style=discord.ButtonStyle.success
    )
    async def confirm(
        self,
        interaction,
        button
    ):

        product = PRODUCTS.get(
            self.product_id
        )

        if not product:

            await interaction.response.edit_message(
                content="❌ المنتج غير موجود.",
                embed=None,
                view=None
            )

            return

        price = product["price"]

        transfer_amount = calculate_transfer_amount(
            price
        )

        tax_amount = (
            transfer_amount - price
        )

        # -------------------------------------------------
        # منع بدء شراء يوزر إذا الستوك فاضي
        # -------------------------------------------------

        if self.product_id in USERNAME_PRODUCTS:

            if get_stock_count(
                self.product_id
            ) <= 0:

                await interaction.response.edit_message(
                    embed=discord.Embed(
                        title="❌ المخزون نفد",
                        description=(
                            "هذا المنتج غير متوفر حاليًا."
                        ),
                        color=0xE74C3C
                    ),
                    view=None
                )

                return

        # -------------------------------------------------
        # أول رد للتفاعل
        # -------------------------------------------------

        await interaction.response.edit_message(
            embed=discord.Embed(
                title="💳 تجهيز الدفع",
                description=(
                    f"📦 المنتج: **{product['name']}**\n\n"

                    f"💰 السعر الأساسي: "
                    f"`{price:,}` كريدت\n"

                    f"🧾 ضريبة ProBot: "
                    f"`{tax_amount:,}` كريدت\n\n"

                    f"💳 المبلغ المطلوب: "
                    f"`{transfer_amount:,}` كريدت\n\n"

                    "سيتم إرسال تعليمات التحويل الآن."
                ),
                color=0xF1C40F
            ),
            view=None
        )

        # -------------------------------------------------
        # انتظار تحويل ProBot
        # -------------------------------------------------

        payment_success = await wait_for_payment(
            interaction,
            product
        )

        if not payment_success:

            return

        # -------------------------------------------------
        # نجاح الدفع
        # -------------------------------------------------

        # =================================================
        # 👤 اليوزر
        # =================================================

        if self.product_id in USERNAME_PRODUCTS:

            async with purchase_lock:

                username = reserve_username(
                    self.product_id
                )

                if username is None:

                    await interaction.channel.send(
                        embed=discord.Embed(
                            title="❌ المخزون نفد",
                            description=(
                                "تم التحقق من الدفع، لكن للأسف "
                                "نفد الستوك قبل التسليم.\n\n"
                                f"تواصل مع <@{OWNER_ID}>."
                            ),
                            color=0xE74C3C
                        )
                    )

                    return

                try:

                    dm = await interaction.user.create_dm()

                    variants = generate_username_variants(
                        username
                    )

                    variants = variants[:100]

                    variant_text = "\n".join(
                        f"`{variant}`"
                        for variant in variants
                    )

                    dm_embed = discord.Embed(
                        title="🎁 تم تسليم طلبك",
                        description=(
                            "شكرًا لشرائك من المتجر ❤️\n\n"
                            f"📦 النوع: **{product['name']}**\n\n"
                            "🔤 اليوزر:\n"
                            f"`{username}`\n\n"
                            "🔀 احتمالات الصيغة:\n"
                            f"{variant_text}\n\n"
                            f"للدعم: <@{OWNER_ID}>"
                        ),
                        color=0x2ECC71
                    )

                    await dm.send(
                        embed=dm_embed
                    )

                except discord.Forbidden:

                    return_username(
                        self.product_id,
                        username
                    )

                    await interaction.channel.send(
                        embed=discord.Embed(
                            title="❌ تعذر إرسال اليوزر",
                            description=(
                                f"{interaction.user.mention}\n\n"
                                "افتح الخاص من أعضاء السيرفر "
                                "ثم تواصل مع صاحب المتجر.\n"
                                f"<@{OWNER_ID}>"
                            ),
                            color=0xE74C3C
                        )
                    )

                    return

                cursor.execute(
                    """
                    INSERT INTO orders
                    (
                        user_id,
                        product_id,
                        product_name,
                        price,
                        delivered_product,
                        created_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        interaction.user.id,
                        self.product_id,
                        product["name"],
                        price,
                        username,
                        datetime.now().isoformat()
                    )
                )

                db.commit()

                await interaction.channel.send(
                    embed=discord.Embed(
                        title="✅ تمت عملية الشراء",
                        description=(
                            f"{interaction.user.mention}\n\n"
                            f"📦 المنتج: **{product['name']}**\n"
                            f"💰 السعر الأساسي: `{price:,}` كريدت\n"
                            f"🧾 الضريبة: `{tax_amount:,}` كريدت\n"
                            f"💳 المدفوع: `{transfer_amount:,}` كريدت\n\n"
                            "📩 تم إرسال اليوزر إلى الخاص."
                        ),
                        color=0x2ECC71
                    )
                )

                try:

                    owner = await bot.fetch_user(
                        OWNER_ID
                    )

                    await owner.send(
                        "🛒 **طلب يوزر جديد**\n\n"
                        f"👤 العميل: {interaction.user}\n"
                        f"🆔 ID: `{interaction.user.id}`\n"
                        f"📦 النوع: **{product['name']}**\n"
                        f"🔤 اليوزر: `{username}`\n"
                        f"💰 السعر الأساسي: `{price:,}`\n"
                        f"🧾 الضريبة: `{tax_amount:,}`\n"
                        f"💳 المدفوع: `{transfer_amount:,}`"
                    )

                except discord.HTTPException:
                    pass

            return

        # =================================================
        # 🤖 البوتات
        # =================================================

        if self.product_id in BOT_PRODUCTS:

            cursor.execute(
                """
                INSERT INTO orders
                (
                    user_id,
                    product_id,
                    product_name,
                    price,
                    delivered_product,
                    created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    interaction.user.id,
                    self.product_id,
                    product["name"],
                    price,
                    "بانتظار التنفيذ",
                    datetime.now().isoformat()
                )
            )

            db.commit()

            await interaction.channel.send(
                embed=discord.Embed(
                    title="✅ تم التحويل بنجاح",
                    description=(
                        f"{interaction.user.mention}\n\n"
                        f"📦 الطلب: **{product['name']}**\n"
                        f"💰 السعر الأساسي: `{price:,}` كريدت\n"
                        f"🧾 الضريبة: `{tax_amount:,}` كريدت\n"
                        f"💳 المدفوع: `{transfer_amount:,}` كريدت\n\n"
                        f"📸 الرجاء التواصل مع "
                        f"<@{OWNER_ID}>\n"
                        "وإرسال **صورة دليل الشراء** "
                        "حتى يتم تنفيذ طلبك."
                    ),
                    color=0x2ECC71
                )
            )

            try:

                owner = await bot.fetch_user(
                    OWNER_ID
                )

                await owner.send(
                    "🛒 **طلب بوت جديد**\n\n"
                    f"👤 العميل: {interaction.user}\n"
                    f"🆔 ID: `{interaction.user.id}`\n"
                    f"📦 المنتج: **{product['name']}**\n"
                    f"💰 السعر الأساسي: `{price:,}`\n"
                    f"🧾 الضريبة: `{tax_amount:,}`\n"
                    f"💳 المدفوع: `{transfer_amount:,}`"
                )

            except discord.HTTPException:
                pass

            return

        # =================================================
        # 🛠️ الأدوات
        # =================================================

        cursor.execute(
            """
            INSERT INTO orders
            (
                user_id,
                product_id,
                product_name,
                price,
                delivered_product,
                created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                interaction.user.id,
                self.product_id,
                product["name"],
                price,
                "بانتظار التنفيذ",
                datetime.now().isoformat()
            )
        )

        db.commit()

        await interaction.channel.send(
            embed=discord.Embed(
                title="✅ تم التحويل بنجاح",
                description=(
                    f"{interaction.user.mention}\n\n"
                    f"📦 المنتج: **{product['name']}**\n"
                    f"💰 السعر الأساسي: `{price:,}` كريدت\n"
                    f"🧾 الضريبة: `{tax_amount:,}` كريدت\n"
                    f"💳 المدفوع: `{transfer_amount:,}` كريدت\n\n"
                    f"📸 الرجاء التواصل مع "
                    f"<@{OWNER_ID}>\n"
                    "وإرسال **صورة دليل الشراء** "
                    "حتى يتم تنفيذ طلبك."
                ),
                color=0x2ECC71
            )
        )

        try:

            owner = await bot.fetch_user(
                OWNER_ID
            )

            await owner.send(
                "🛒 **طلب أداة جديد**\n\n"
                f"👤 العميل: {interaction.user}\n"
                f"🆔 ID: `{interaction.user.id}`\n"
                f"📦 المنتج: **{product['name']}**\n"
                f"💰 السعر الأساسي: `{price:,}`\n"
                f"🧾 الضريبة: `{tax_amount:,}`\n"
                f"💳 المدفوع: `{transfer_amount:,}`"
            )

        except discord.HTTPException:
            pass

    @discord.ui.button(
        label="إلغاء",
        emoji="❌",
        style=discord.ButtonStyle.danger
    )
    async def cancel(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            embed=discord.Embed(
                title="❌ تم إلغاء العملية",
                description=(
                    "لم يتم إجراء أي تحويل."
                ),
                color=0xE74C3C
            ),
            view=None
        )


# =========================================================
# 🛒 !قائمة
# =========================================================

@bot.command(name="قائمة")
async def store(ctx):

    try:

        await ctx.message.delete()

    except discord.HTTPException:
        pass

    # -----------------------------------------------------
    # طلب ID
    # -----------------------------------------------------

    await ctx.send(
        content=ctx.author.mention,
        embed=discord.Embed(
            title="🆔 التحقق من الهوية",
            description=(
                "قبل الدخول إلى المتجر، "
                "الرجاء إرسال **Discord ID الخاص بك**.\n\n"
                "مثال:\n"
                "`123456789012345678`\n\n"
                "⏱️ لديك 60 ثانية."
            ),
            color=0x3498DB
        )
    )

    def check(message):

        if message.author.id != ctx.author.id:
            return False

        if message.channel.id != ctx.channel.id:
            return False

        return message.content.strip().isdigit()

    try:

        id_message = await bot.wait_for(
            "message",
            timeout=60,
            check=check
        )

    except asyncio.TimeoutError:

        await ctx.send(
            f"⏰ {ctx.author.mention} انتهى وقت إدخال الـID.",
            delete_after=10
        )

        return

    entered_id = int(
        id_message.content.strip()
    )

    # -----------------------------------------------------
    # لازم يكون ID الشخص نفسه
    # -----------------------------------------------------

    if entered_id != ctx.author.id:

        await ctx.send(
            f"❌ {ctx.author.mention}\n"
            "الـID الذي أرسلته لا يطابق حسابك.",
            delete_after=10
        )

        return

    verified_users.add(
        ctx.author.id
    )

    try:

        await id_message.delete()

    except discord.HTTPException:
        pass

    await ctx.send(
        embed=main_embed(),
        view=MainMenuView(
            ctx.author.id
        )
    )


# =========================================================
# 📖 !مساعدة
# =========================================================

@bot.command(name="مساعدة")
async def help_command(ctx):

    embed = discord.Embed(
        title="📖 أوامر المتجر",
        description=(
            "الأوامر المتاحة:"
        ),
        color=0x3498DB
    )

    embed.add_field(
        name="🛒 !قائمة",
        value=(
            "فتح المتجر وبدء عملية الشراء."
        ),
        inline=False
    )

    embed.add_field(
        name="💳 الدفع",
        value=(
            "الدفع يتم عن طريق ProBot."
        ),
        inline=False
    )

    await ctx.send(
        embed=embed
    )


# =========================================================
# ❌ أخطاء الأوامر
# =========================================================

@bot.event
async def on_command_error(
    ctx,
    error
):

    if isinstance(
        error,
        commands.CommandNotFound
    ):

        return

    if isinstance(
        error,
        commands.MissingRequiredArgument
    ):

        await ctx.send(
            "❌ الأمر ناقص معلومات.",
            delete_after=5
        )

        return

    if isinstance(
        error,
        commands.BadArgument
    ):

        await ctx.send(
            "❌ تأكد من البيانات.",
            delete_after=5
        )

        return

    print(
        f"[ERROR] {type(error).__name__}: {error}"
    )


# =========================================================
# 🟢 تشغيل البوت
# =========================================================

@bot.event
async def on_ready():

    print(
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )

    print(
        f"✅ البوت يعمل: {bot.user}"
    )

    print(
        f"🆔 ID: {bot.user.id}"
    )

    print(
        "🛒 المتجر جاهز"
    )

    print(
        "👤 الستوك جاهز"
    )

    print(
        "💳 الدفع عبر ProBot جاهز"
    )

    print(
        "⏱️ مهلة الدفع: 15 دقيقة"
    )

    print(
        "🧾 ضريبة ProBot: 5%"
    )

    print(
        f"🤖 ProBot ID: {PROBOT_ID}"
    )

    print(
        f"💰 المستلم: {OWNER_ID}"
    )

    print(
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )

    await bot.change_presence(
        activity=discord.Game(
            name="!قائمة 🛒"
        )
    )


# =========================================================
# 🔑 TOKEN
# =========================================================

TOKEN = os.getenv("TOKEN")

if not TOKEN:

    raise RuntimeError(
        "❌ لم يتم العثور على TOKEN في Railway Variables."
    )


bot.run(TOKEN)
