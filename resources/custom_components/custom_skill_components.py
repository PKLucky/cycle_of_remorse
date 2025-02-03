from __future__ import annotations

from app.data.database.components import ComponentType
from app.data.database.database import DB
from app.data.database.skill_components import SkillComponent, SkillTags
from app.engine import (action, banner, combat_calcs, engine, equations,
                        image_mods, item_funcs, item_system, skill_system,
                        target_system)
from app.engine.game_state import game
from app.engine.combat import playback as pb
from app.engine.objects.unit import UnitObject
from app.utilities import utils, static_random


class DoNothing(SkillComponent):
    nid = 'do_nothing'
    desc = 'does nothing'
    tag = SkillTags.CUSTOM

    expose = ComponentType.Int
    value = 1

class AdditionalInventorySpace(SkillComponent):
    nid = 'additional_inventory_space'
    desc = "Unit can hold additional items"
    tag = SkillTags.CUSTOM

    expose = ComponentType.Int
    value = 1

    def num_items_offset(self, unit) -> int:
        return self.value
    
class Degeneration(SkillComponent):
    nid = 'degeneration'
    desc = "Unit loses %% of HP at beginning of turn."
    tag = SkillTags.CUSTOM

    expose = ComponentType.Float
    value = 0.2

    def on_upkeep(self, actions, playback, unit):
        max_hp = equations.parser.hitpoints(unit)
        hp_change = int(max_hp * self.value)
        actions.append(action.ChangeHP(unit, -hp_change))
        # Playback
        playback.append(pb.DamageNumbers(unit, hp_change))

class EvalResist(SkillComponent):
    nid = 'eval_resist'
    desc = "Gives +X damage resist solved using evaluate"
    tag = SkillTags.CUSTOM

    expose = ComponentType.String

    def modify_resist(self, unit, item_to_avoid):
        from app.engine import evaluate
        try:
            return int(evaluate.evaluate(self.value, unit, local_args={'item_to_avoid': item_to_avoid}))
        except Exception as e:
            logging.error("Couldn't evaluate %s conditional (%s)", self.value, e)
        return 0
