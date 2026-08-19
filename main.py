import discord
from discord.ext import commands
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import os
import asyncio


# =========================================================
# ⚙️ إعدادات المتجر
# =========================================================

OWNER_ID = 1531438534244700313
PREFIX = "!"


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
    }
}


USERNAME_PRODUCTS = {
    "username_5",
    "username_4",
    "username_3",
    "username_2"
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
# 🗄️ PostgreSQL — Railway
# =========================================================

# التعديل الوحيد هنا:
# يحاول DATABASE_URL أولًا، ثم DATABASE_PRIVATE_URL،
# ثم DATABASE_PUBLIC_URL، ثم يبني الرابط من متغيرات PostgreSQL.

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
        "❌ لم يتم العثور على DATABASE_URL أو بيانات PostgreSQL في Railway Variables."
    )


db = psycopg2.connect(DATABASE_URL)

db.autocommit = False

cursor = db.cursor(
    cursor_factory=RealDictCursor
)


# =========================================================
# 🧱 إنشاء الجداول
# =========================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    credits BIGINT NOT NULL DEFAULT 0
)
""")

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
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    amount BIGINT NOT NULL,
    transaction_type TEXT NOT NULL,
    description TEXT NOT NULL,
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
# 📥 تحميل المخزون إلى PostgreSQL
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
# 💳 نظام الكريدت
# =========================================================

def ensure_user(user_id):

    cursor.execute(
        """
        SELECT user_id
        FROM users
        WHERE user_id = %s
        """,
        (user_id,)
    )

    if cursor.fetchone() is None:

        cursor.execute(
            """
            INSERT INTO users
            (
                user_id,
                credits
            )
            VALUES (%s, 0)
            ON CONFLICT (user_id) DO NOTHING
            """,
            (user_id,)
        )

        db.commit()


def get_credits(user_id):

    ensure_user(user_id)

    cursor.execute(
        """
        SELECT credits
        FROM users
        WHERE user_id = %s
        """,
        (user_id,)
    )

    result = cursor.fetchone()

    return result["credits"] if result else 0


def add_credits(
    user_id,
    amount,
    description="إضافة كريدت"
):

    if amount <= 0:
        return False

    ensure_user(user_id)

    cursor.execute(
        """
        UPDATE users
        SET credits = credits + %s
        WHERE user_id = %s
        """,
        (
            amount,
            user_id
        )
    )

    cursor.execute(
        """
        INSERT INTO transactions
        (
            user_id,
            amount,
            transaction_type,
            description,
            created_at
        )
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            user_id,
            amount,
            "ADD",
            description,
            datetime.now().isoformat()
        )
    )

    db.commit()

    return True


def remove_credits(
    user_id,
    amount,
    description="شراء"
):

    if amount <= 0:
        return False

    ensure_user(user_id)

    cursor.execute(
        """
        UPDATE users
        SET credits = credits - %s
        WHERE user_id = %s
        AND credits >= %s
        """,
        (
            amount,
            user_id,
            amount
        )
    )

    if cursor.rowcount == 0:
        return False

    cursor.execute(
        """
        INSERT INTO transactions
        (
            user_id,
            amount,
            transaction_type,
            description,
            created_at
        )
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            user_id,
            -amount,
            "PURCHASE",
            description,
            datetime.now().isoformat()
        )
    )

    db.commit()

    return True


# =========================================================
# 🔀 توليد احتمالات اليوزر
# =========================================================

def generate_username_variants(username):

    variants = set()

    variants.add(username)

    for i in range(1, len(username)):

        variants.add(
            username[:i] + "." + username[i:]
        )

        variants.add(
            username[:i] + "_" + username[i:]
        )

    if len(username) >= 3:

        for i in range(1, len(username)):

            for j in range(i + 1, len(username)):

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

                variants.add(
                    username[:i]
                    + "._"
                    + username[i:j]
                    + username[j:]
                )

                variants.add(
                    username[:i]
                    + "_."
                    + username[i:j]
                    + username[j:]
                )

    return list(variants)


# =========================================================
# 📦 سحب يوزر من المخزون
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
        return None

    db.commit()

    return row["username"]


# =========================================================
# 📊 عدد المخزون
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
        name="💳 رصيدك",
        value="استخدم `!رصيدي` لمعرفة رصيدك.",
        inline=False
    )

    embed.add_field(
        name="📝 طلب آخر",
        value=f"للطلبات الأخرى تواصل مع <@{OWNER_ID}>.",
        inline=False
    )

    embed.set_footer(
        text="متجر الخدمات • نظام الكريدت"
    )

    return embed


# =========================================================
# 🏠 القائمة الرئيسية
# =========================================================

class MainMenuView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(
        label="شراء يوزرات",
        emoji="👤",
        style=discord.ButtonStyle.primary
    )
    async def usernames(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        embed = discord.Embed(
            title="👤 شراء يوزرات",
            description="اختر نوع اليوزر الذي تريده:",
            color=0x3498DB
        )

        await interaction.response.edit_message(
            embed=embed,
            view=ProductsView("يوزرات")
        )

    @discord.ui.button(
        label="شراء أدوات",
        emoji="🛠️",
        style=discord.ButtonStyle.success
    )
    async def tools(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        embed = discord.Embed(
            title="🛠️ شراء أدوات",
            description="اختر الأداة التي تريد شراءها:",
            color=0x9B59B6
        )

        await interaction.response.edit_message(
            embed=embed,
            view=ProductsView("أدوات")
        )

    @discord.ui.button(
        label="رصيدي",
        emoji="💳",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def balance_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        credits = get_credits(
            interaction.user.id
        )

        embed = discord.Embed(
            title="💳 رصيدك",
            description=(
                "رصيدك الحالي:\n\n"
                f"# `{credits:,}` كريدت"
            ),
            color=0x2ECC71
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    @discord.ui.button(
        label="طلب آخر",
        emoji="📝",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def other(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        embed = discord.Embed(
            title="📝 طلب آخر",
            description=(
                f"للطلبات الأخرى تواصل مع <@{OWNER_ID}>."
            ),
            color=0xF1C40F
        )

        await interaction.response.edit_message(
            embed=embed,
            view=OtherRequestView()
        )


# =========================================================
# 📝 طلب آخر
# =========================================================

class OtherRequestView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(
        label="رجوع",
        emoji="⬅️",
        style=discord.ButtonStyle.secondary
    )
    async def back(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.edit_message(
            embed=main_embed(),
            view=MainMenuView()
        )


# =========================================================
# 📦 قائمة المنتجات
# =========================================================

class ProductsView(discord.ui.View):

    def __init__(self, category):

        super().__init__(timeout=300)

        products = [
            (product_id, product)
            for product_id, product in PRODUCTS.items()
            if product["category"] == category
        ]

        for product_id, product in products:

            label = (
                f"{product['name']} • "
                f"{product['price']:,}"
            )

            if product_id in USERNAME_PRODUCTS:

                stock_count = get_stock_count(
                    product_id
                )

                label = (
                    f"{product['name']} • "
                    f"{product['price']:,} • "
                    f"متوفر: {stock_count}"
                )

            button = discord.ui.Button(
                label=label[:80],
                style=discord.ButtonStyle.primary
            )

            async def callback(
                interaction: discord.Interaction,
                pid=product_id
            ):

                product_data = PRODUCTS.get(pid)

                if product_data is None:

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

                balance = get_credits(
                    interaction.user.id
                )

                if balance >= product_data["price"]:
                    status = "✅ الرصيد كافٍ"
                else:
                    status = "❌ الرصيد غير كافٍ"

                embed = discord.Embed(
                    title="🛒 تأكيد الطلب",
                    description="راجع بيانات الطلب قبل التأكيد:",
                    color=0x3498DB
                )

                embed.add_field(
                    name="📦 المنتج",
                    value=product_data["name"],
                    inline=False
                )

                embed.add_field(
                    name="💰 السعر",
                    value=(
                        f"`{product_data['price']:,}` كريدت"
                    ),
                    inline=True
                )

                embed.add_field(
                    name="💳 رصيدك",
                    value=f"`{balance:,}` كريدت",
                    inline=True
                )

                embed.add_field(
                    name="📊 الحالة",
                    value=status,
                    inline=False
                )

                await interaction.response.edit_message(
                    embed=embed,
                    view=ConfirmView(
                        pid,
                        interaction.user.id
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
            interaction: discord.Interaction
        ):

            await interaction.response.edit_message(
                embed=main_embed(),
                view=MainMenuView()
            )

        back.callback = back_callback

        self.add_item(back)


# =========================================================
# ✅ تأكيد الشراء
# =========================================================

class ConfirmView(discord.ui.View):

    def __init__(
        self,
        product_id,
        buyer_id
    ):

        super().__init__(timeout=60)

        self.product_id = product_id
        self.buyer_id = buyer_id

    async def interaction_check(
        self,
        interaction: discord.Interaction
    ):

        if interaction.user.id != self.buyer_id:

            await interaction.response.send_message(
                "❌ هذه العملية ليست لك.",
                ephemeral=True
            )

            return False

        return True

    @discord.ui.button(
        label="تأكيد الشراء",
        emoji="✅",
        style=discord.ButtonStyle.success
    )
    async def confirm(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        product = PRODUCTS.get(
            self.product_id
        )

        if product is None:

            await interaction.response.edit_message(
                content="❌ المنتج غير موجود.",
                embed=None,
                view=None
            )

            return

        price = product["price"]

        # =================================================
        # 👤 شراء يوزر
        # =================================================

        if self.product_id in USERNAME_PRODUCTS:

            async with purchase_lock:

                balance = get_credits(
                    interaction.user.id
                )

                if balance < price:

                    await interaction.response.edit_message(
                        embed=discord.Embed(
                            title="❌ الرصيد غير كافٍ",
                            description=(
                                f"📦 المنتج: **{product['name']}**\n"
                                f"💰 السعر: `{price:,}` كريدت\n"
                                f"💳 رصيدك: `{balance:,}` كريدت"
                            ),
                            color=0xE74C3C
                        ),
                        view=None
                    )

                    return

                username = reserve_username(
                    self.product_id
                )

                if username is None:

                    await interaction.response.edit_message(
                        embed=discord.Embed(
                            title="❌ المخزون نفد",
                            description=(
                                f"مخزون **{product['name']}** نفد حاليًا.\n\n"
                                "لم يتم خصم أي كريدت."
                            ),
                            color=0xE74C3C
                        ),
                        view=None
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
                            "🔤 احتمالات اليوزر:\n\n"
                            f"{variant_text}\n\n"
                            "⚠️ هذه احتمالات للصيغة وليست ضمانًا "
                            "لتوفرها أو صلاحيتها.\n\n"
                            "إذا لم يعمل معك أي احتمال، "
                            "تواصل مع صاحب المتجر في الخاص:\n"
                            f"<@{OWNER_ID}>"
                        ),
                        color=0x2ECC71
                    )

                    await dm.send(
                        embed=dm_embed
                    )

                except discord.Forbidden:

                    cursor.execute(
                        """
                        UPDATE username_stock
                        SET sold = 0
                        WHERE product_id = %s
                        AND username = %s
                        """,
                        (
                            self.product_id,
                            username
                        )
                    )

                    db.commit()

                    await interaction.response.edit_message(
                        embed=discord.Embed(
                            title="❌ لا يمكن إرسال الخاص",
                            description=(
                                "افتح الرسائل الخاصة من السيرفر "
                                "ثم حاول مرة أخرى.\n\n"
                                "لم يتم خصم أي كريدت."
                            ),
                            color=0xE74C3C
                        ),
                        view=None
                    )

                    return

                success = remove_credits(
                    interaction.user.id,
                    price,
                    f"شراء {product['name']}"
                )

                if not success:

                    cursor.execute(
                        """
                        UPDATE username_stock
                        SET sold = 0
                        WHERE product_id = %s
                        AND username = %s
                        """,
                        (
                            self.product_id,
                            username
                        )
                    )

                    db.commit()

                    await interaction.response.edit_message(
                        content="❌ تعذر إتمام عملية الخصم.",
                        embed=None,
                        view=None
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

                new_balance = get_credits(
                    interaction.user.id
                )

                await interaction.response.edit_message(
                    embed=discord.Embed(
                        title="✅ تمت عملية الشراء",
                        description=(
                            "تم إرسال اليوزر إلى الخاص بنجاح! 🎉\n\n"
                            f"📦 المنتج: **{product['name']}**\n"
                            f"💰 السعر: `{price:,}` كريدت\n"
                            f"💳 رصيدك الجديد: `{new_balance:,}` كريدت\n\n"
                            "📩 راجع الخاص للحصول على طلبك."
                        ),
                        color=0x2ECC71
                    ),
                    view=None
                )

                try:

                    owner = await bot.fetch_user(
                        OWNER_ID
                    )

                    await owner.send(
                        "🛒 **طلب يوزر جديد**\n\n"
                        f"👤 العميل: {interaction.user.mention}\n"
                        f"🆔 ID: `{interaction.user.id}`\n"
                        f"📦 النوع: **{product['name']}**\n"
                        f"🔤 اليوزر الخام: `{username}`\n"
                        f"💰 السعر: `{price:,}` كريدت"
                    )

                except discord.HTTPException:
                    pass

            return

        # =================================================
        # 🛠️ شراء أداة
        # =================================================

        async with purchase_lock:

            balance = get_credits(
                interaction.user.id
            )

            if balance < price:

                await interaction.response.edit_message(
                    embed=discord.Embed(
                        title="❌ الرصيد غير كافٍ",
                        description=(
                            f"📦 المنتج: **{product['name']}**\n"
                            f"💰 السعر: `{price:,}` كريدت\n"
                            f"💳 رصيدك: `{balance:,}` كريدت"
                        ),
                        color=0xE74C3C
                    ),
                    view=None
                )

                return

            success = remove_credits(
                interaction.user.id,
                price,
                f"شراء {product['name']}"
            )

            if not success:

                await interaction.response.edit_message(
                    content="❌ تعذر إتمام عملية الخصم.",
                    embed=None,
                    view=None
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
                    "تسليم يدوي عبر المالك",
                    datetime.now().isoformat()
                )
            )

            db.commit()

            new_balance = get_credits(
                interaction.user.id
            )

            try:

                dm = await interaction.user.create_dm()

                await dm.send(
                    embed=discord.Embed(
                        title="✅ تم الدفع بنجاح",
                        description=(
                            f"📦 المنتج: **{product['name']}**\n\n"
                            "تم تسجيل طلبك بنجاح. 🎉\n\n"
                            "📩 لاستلام الأداة، "
                            "تواصل مع صاحب المتجر في الخاص:\n"
                            f"<@{OWNER_ID}>"
                        ),
                        color=0x2ECC71
                    )
                )

            except discord.Forbidden:

                await interaction.response.edit_message(
                    embed=discord.Embed(
                        title="⚠️ تم تسجيل الطلب",
                        description=(
                            "تم تسجيل عملية الشراء، لكن تعذر إرسال "
                            "رسالة الخاص.\n\n"
                            f"تواصل مع <@{OWNER_ID}> لاستلام طلبك."
                        ),
                        color=0xF1C40F
                    ),
                    view=None
                )

                return

            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="✅ تمت عملية الشراء",
                    description=(
                        "تم الدفع بنجاح! 🎉\n\n"
                        f"📦 المنتج: **{product['name']}**\n"
                        f"💰 السعر: `{price:,}` كريدت\n"
                        f"💳 رصيدك الجديد: `{new_balance:,}` كريدت\n\n"
                        f"📩 راجع الخاص، ثم تواصل مع "
                        f"<@{OWNER_ID}> لاستلام الأداة."
                    ),
                    color=0x2ECC71
                ),
                view=None
            )

            try:

                owner = await bot.fetch_user(
                    OWNER_ID
                )

                await owner.send(
                    "🛠️ **طلب أداة جديد**\n\n"
                    f"👤 العميل: {interaction.user.mention}\n"
                    f"🆔 ID: `{interaction.user.id}`\n"
                    f"📦 الأداة: **{product['name']}**\n"
                    f"💰 السعر: `{price:,}` كريدت"
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
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        embed = discord.Embed(
            title="❌ تم إلغاء العملية",
            description="لم يتم خصم أي كريدت من رصيدك.",
            color=0xE74C3C
        )

        await interaction.response.edit_message(
            embed=embed,
            view=None
        )


# =========================================================
# 🛒 أمر !قائمة
# =========================================================

@bot.command(name="قائمة")
async def store(ctx):

    try:
        await ctx.message.delete()
    except discord.HTTPException:
        pass

    await ctx.send(
        embed=main_embed(),
        view=MainMenuView()
    )


# =========================================================
# 💳 أمر !رصيدي
# =========================================================

@bot.command(name="رصيدي")
async def balance(ctx):

    credits = get_credits(
        ctx.author.id
    )

    embed = discord.Embed(
        title="💳 رصيدك",
        description=(
            "رصيدك الحالي:\n\n"
            f"# `{credits:,}` كريدت"
        ),
        color=0x2ECC71
    )

    await ctx.send(
        embed=embed
    )


# =========================================================
# ➕ أمر !اضافة
# =========================================================

@bot.command(name="اضافة")
async def add_credits_command(
    ctx,
    member: discord.Member = None,
    amount: int = None
):

    if ctx.author.id != OWNER_ID:

        await ctx.send(
            "❌ هذا الأمر مخصص لصاحب المتجر.",
            delete_after=5
        )

        return

    if member is None or amount is None:

        await ctx.send(
            "❌ الاستخدام:\n"
            "`!اضافة @العضو المبلغ`",
            delete_after=7
        )

        return

    if amount <= 0:

        await ctx.send(
            "❌ المبلغ يجب أن يكون أكبر من صفر.",
            delete_after=5
        )

        return

    add_credits(
        member.id,
        amount,
        "إضافة بواسطة المالك"
    )

    await ctx.send(
        f"✅ تمت إضافة `{amount:,}` كريدت إلى "
        f"{member.mention}\n"
        f"💳 الرصيد الجديد: "
        f"`{get_credits(member.id):,}`"
    )


# =========================================================
# ➖ أمر !خصم
# =========================================================

@bot.command(name="خصم")
async def remove_credits_command(
    ctx,
    member: discord.Member = None,
    amount: int = None
):

    if ctx.author.id != OWNER_ID:

        await ctx.send(
            "❌ هذا الأمر مخصص لصاحب المتجر.",
            delete_after=5
        )

        return

    if member is None or amount is None:

        await ctx.send(
            "❌ الاستخدام:\n"
            "`!خصم @العضو المبلغ`",
            delete_after=7
        )

        return

    if amount <= 0:

        await ctx.send(
            "❌ المبلغ يجب أن يكون أكبر من صفر.",
            delete_after=5
        )

        return

    success = remove_credits(
        member.id,
        amount,
        "خصم بواسطة المالك"
    )

    if not success:

        await ctx.send(
            "❌ رصيد العضو غير كافٍ.",
            delete_after=5
        )

        return

    await ctx.send(
        f"✅ تم خصم `{amount:,}` كريدت من "
        f"{member.mention}\n"
        f"💳 الرصيد الجديد: "
        f"`{get_credits(member.id):,}`"
    )


# =========================================================
# 📖 أمر !مساعدة
# =========================================================

@bot.command(name="مساعدة")
async def help_command(ctx):

    embed = discord.Embed(
        title="📖 أوامر المتجر",
        description="الأوامر المتاحة:",
        color=0x3498DB
    )

    embed.add_field(
        name="🛒 !قائمة",
        value="فتح متجر الخدمات.",
        inline=False
    )

    embed.add_field(
        name="💳 !رصيدي",
        value="عرض رصيدك.",
        inline=False
    )

    if ctx.author.id == OWNER_ID:

        embed.add_field(
            name="➕ !اضافة @عضو المبلغ",
            value="إضافة كريدت.",
            inline=False
        )

        embed.add_field(
            name="➖ !خصم @عضو المبلغ",
            value="خصم كريدت.",
            inline=False
        )

    await ctx.send(
        embed=embed
    )


# =========================================================
# ❌ معالجة الأخطاء
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
            "❌ تأكد من الـ Mention والمبلغ.",
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

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"✅ البوت يعمل: {bot.user}")
    print(f"🆔 ID: {bot.user.id}")
    print("🛒 المتجر جاهز")
    print("💳 نظام الكريدت جاهز")
    print("👤 مخزون اليوزرات جاهز")
    print("🛠️ نظام تسليم الأدوات اليدوي جاهز")
    print("🗄️ PostgreSQL جاهزة")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    await bot.change_presence(
        activity=discord.Game(
            name="!قائمة 🛒"
        )
    )


# =========================================================
# 🔑 TOKEN — Railway
# =========================================================

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise RuntimeError(
        "❌ لم يتم العثور على TOKEN في Railway Variables."
    )

bot.run(TOKEN)
