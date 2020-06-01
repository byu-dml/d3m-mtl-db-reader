import json
from typing import List, Dict, Union, Type

from analytics.entities.entity import Entity, EntityWithId
from analytics.entities.dataset import Dataset
from analytics.entities.pipeline import Pipeline
from analytics.entities.pipeline_run import PipelineRun
from analytics.entities.problem.problem import Problem

_test_entity_names: Dict[str, Dict[str, Union[Type[Entity], List[str]]]] = {
    "pipelines": {
        "type": Pipeline,
        "names": [
            "simple_pipeline_a",
            "simple_pipeline_b",
            "pipeline_with_subpipelines",
            "simple_pipeline_b_one_off",
            "pipeline_with_edges",
            "similar_pipeline_a",  # A and B are off by only one primitive
            "similar_pipeline_b",
            "similar_pipeline_c",  # C and D are off by only one primitive, and
            "similar_pipeline_d",  # the primitives they differ by are named such
            # that the order of the two runs should be
            # swapped when creating a diff entry
        ],
    },
    "pipeline_runs": {
        "type": PipelineRun,
        "names": [
            "similar_pipeline_run_a",
            "similar_pipeline_run_b",
            "similar_pipeline_run_c",
            "similar_pipeline_run_d",
            "invalid_pipeline_run_a",  # Has a state of FAILURE
            "invalid_pipeline_run_b",  # Has no predictions
            "invalid_pipeline_run_c",  # Phase is FIT, not PRODUCE
            "invalid_pipeline_run_d",  # Problem task type is unsupported
        ],
    },
    "problems": {
        "type": Problem,
        "names": [
            "problem_a",
            "problem_b",
            "invalid_problem_b",  # Problem task type is unsupported
        ],
    },
    "datasets": {"type": Dataset, "names": ["dataset_a", "dataset_b"]},
}

_test_data_path: str = "./tests/data"
_test_data_ext: str = ".json"


def load_test_entities() -> Dict[str, Dict[str, Entity]]:
    """
    Loads the test data entities from their JSON representations.

    Returns
    -------
    A dictionary mapping the names of entity types to dictionaries
    containing the entities.
    """
    entities: Dict[str, Dict[str, Entity]] = {}

    for entity_type, entity_names in _test_entity_names.items():
        entities[entity_type] = {}

        for name in entity_names["names"]:
            with open(f"{_test_data_path}/{name}{_test_data_ext}", "r") as f:
                entity_dict: dict = json.load(f)
                entity = entity_names["type"](
                    entity_dict, run_predictions_path=_test_data_path + "/predictions"
                )

                if entity_names["type"] == PipelineRun:
                    entities[entity_type][entity.id] = entity
                else:
                    entities[entity_type][entity.digest] = entity

    return entities


def post_init(maps: Dict[str, Dict[str, EntityWithId]]) -> None:
    """
    Calls post_init() on every Entity in maps. Because many entities
    reference other entities, some of their construction can't be
    performed until all entities have been loaded. This function
    allows them to perform any remaining operations.
    """
    for entities in maps.values():
        for entity in entities.values():
            entity.post_init(maps)
