from click import group
from telebot.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from database import crud
from missedbot import bot
from model import discipline, student

_student_missed: list[int] = []
PAGINATOR = 5
__report_prefix = [
    "presenceDis_",
    "presenceGroup_",
    "studClick_",
]


def __is_prefix_callback(data: str) -> bool:
    """Проверяет, является ли данная строка префиксом любого
    из элементов списка '__report_prefix'.
    """
    for it in __report_prefix:
        if it in data:
            return True
    return False


@bot.message_handler(
    is_admin=True,
    commands=["presencecheck"],
)
async def handle_presence_check(message: Message):
    await presence_check(message)


@bot.message_handler(
    is_admin=True,
    commands=["presencecheck"],
)
async def handle_no_presence_check(message: Message):
    await bot.send_message(message.chat.id, "Ты кто? Oo")


async def presence_check(message: Message):
    """
    Отправляет сообщение с перечнем дисциплин и их ID в виде
    кнопок типа Inline. Пользователь может выбрать дисциплину,
    нажав на соответствующую кнопку. Выбранный ID дисциплины
    передается в виде callback-данных в функцию, указанную
    в поле "callback_data" кнопки.
    """
    disciplines = crud.get_assigned_group()
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        *[
            InlineKeyboardButton(
                it.name,
                callback_data=f"presenceDis_{it.id}",
            )
            for it in disciplines
        ]
    )
    await bot.send_message(
        message.chat.id,
        "Выберите дисциплину:",
        reply_markup=markup,
    )


@bot.callback_query_handler(
    func=lambda call: __is_prefix_callback(call.data),
)
async def callback_presence_check(call):
    type_callback = call.data.split("_")[0]
    match type_callback:
        case "presenceDis":
            discipline_id = int(call.data.split("_")[1])
            groups = crud.get_assigned_group(discipline_id)
            markup = InlineKeyboardMarkup()
            markup.row_width = 1
            markup.add(
                *[
                    InlineKeyboardButton(
                        it.name,
                        callback_data=f"presenceGroup_0_{discipline_id}_{it.id}",
                    )
                    for it in groups
                ]
            )
            _student_missed.clear()
            await bot.edit_message_text(
                "Выберите группу:",
                call.message.chat.id,
                call.message.id,
                reply_markup=markup,
            )
        case "presenceGroup" | "studClick":
            paginator = int(call.data.split("_")[1])
            discipline_id = int(call.data.split("_")[2])
            group_id = int(call.data.split("_")[3])
            if type_callback == "studClick":
                student_id = int(call.data.split("_")[4])
                if student_id in _student_missed:
                    _student_missed.remove(student_id)
                else:
                    _student_missed.append(student_id)
                await student_check(
                    call,
                    paginator,
                    discipline_id,
                    group_id,
                )
        case _:
            await bot.edit_message_text(
                "Неизвестный формат для обработки данных",
                call.message.chat.id,
                call.message.id,
            )


async def student_check(
        call,
        paginator: int,
        discipline_id: int,
        group_id: int,
) -> None:
    """Получает список студентов для заданного group_id, пагинирует
    их и выводит с кнопками выбора пропущенных студентов.

    :param call: Callback-запрос от пользователя.
    :param paginator: Целочисленное значение, представляющее
    номер страницы пагинации.
    :param discipline_id: Целочисленное значение, представляющее ID дисциплины.
    :param group_id: Целочисленное значение, представляющее ID группы.
    :return: None
    """
    students = crud.get_assigned_group(group_id)

    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        *[
            InlineKeyboardButton(
                f"+{it.full_name}"
                if it.id not in _student_missed
                else f"-{it.full_name}",
                callback_data=f"studClick_{paginator}_{discipline_id}_{group_id}_{it.id}",
            )
            for it in students[PAGINATOR * paginator : PAGINATOR * (paginator + 1)]
        ]
    )
    if paginator == 0:
        markup.add(
            InlineKeyboardButton(
                "->",
                callback_data=f"presenceGroup_{paginator + 1}_{discipline_id}_{group_id}",
            )
        )
