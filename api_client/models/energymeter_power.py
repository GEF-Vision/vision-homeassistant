from typing import Any, Dict, List, Optional, Type, TypeVar

import attr

T = TypeVar("T", bound="EnergymeterPower")


@attr.s(auto_attribs=True)
class EnergymeterPower:
    """
    Attributes:
        import_ (Optional[int]): Imported power in watts (W).
        export (Optional[int]): Exported power in watts (W).
    """

    import_: Optional[int]
    export: Optional[int]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        import_ = self.import_
        export = self.export

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "import": import_,
                "export": export,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        import_ = d.pop("import")

        export = d.pop("export")

        energymeter_power = cls(
            import_=import_,
            export=export,
        )

        energymeter_power.additional_properties = d
        return energymeter_power

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
