from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove

from exceptions import ScheduleNotFoundError
from keyboards.schedule_choice import schedule_type_choice_keyboard
from repositories import ScheduleRepository, GeneratedScheduleRepository
from utils import parse_group_index

router = Router()


class GetScheduleStatesGroup(StatesGroup):
    entering_group_index = State()
    choosing_schedule_type = State()


@router.message(StateFilter(None), Command("get_schedule"))
async def cmd_get_schedule(message: Message, state: FSMContext):
    await message.answer("Введіть назву вашої групи (наприклад, К228, К-228 або к228)")
    await state.set_state(GetScheduleStatesGroup.entering_group_index)


@router.message(GetScheduleStatesGroup.entering_group_index)
async def get_schedule_choose_schedule_type(message: Message, state: FSMContext):
    await state.update_data(group_index=parse_group_index(message.text))

    schedule_repository = ScheduleRepository()
    async with schedule_repository:
        schedule_types = await schedule_repository.get_schedule_types()

    await message.answer(
        "Який розклад хочете отримати?",
        reply_markup=schedule_type_choice_keyboard(schedule_types),
    )

    await state.set_state(GetScheduleStatesGroup.choosing_schedule_type)


@router.message(GetScheduleStatesGroup.choosing_schedule_type)
async def get_schedule_final_response(message: Message, state: FSMContext):
    user_data = await state.get_data()

    generated_schedule_repository = GeneratedScheduleRepository()
    async with generated_schedule_repository:
        try:
            schedule = await generated_schedule_repository.get_schedule(
                user_data["group_index"], message.text
            )
        except ScheduleNotFoundError:
            await message.answer(
                "Упс, щось пішло не так", reply_markup=ReplyKeyboardRemove()
            )
            await state.clear()
            return

    await message.answer(
        schedule.schedule, parse_mode=ParseMode.HTML, reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()
