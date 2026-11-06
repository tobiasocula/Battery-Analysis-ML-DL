battery_id,
timestamp,
cycle_index,
battery_age_days,
time_since_previous_cycle_hours,
equivalent_full_cycles,
soc_start_pct,
soc_end_pct,
depth_of_discharge_pct,
high_soc_exposure_fraction,
low_soc_exposure_fraction,
charge_c_rate,
discharge_c_rate,
charge_current_a,
discharge_current_a,
charge_duration_min,
discharge_duration_min,
energy_discharged_kwh,
ambient_temp_c,
pack_temp_c,
cumulative_high_temp_hours,
cooling_active,
pack_voltage_mean_v,
pack_voltage_charge_v,
pack_voltage_discharge_v,
state_of_health_pct,
eol_reached,
remaining_useful_cycles,
remaining_useful_efc,
degradation_status,
internal_resistance_mOhm

| Column                          | Approximate meaning                                               |
| ------------------------------- | ----------------------------------------------------------------- |
| battery_id                      | Unique identifier for the individual battery/pack.                |
| timestamp                       | Date and time the cycle began or was recorded.                    |
| cycle_index                     | Sequential cycle number for that battery: 1, 2, 3, etc.           |
| battery_age_days                | Days elapsed since the battery entered service or testing.        |
| time_since_previous_cycle_hours | Rest/idle time between the previous cycle and this one, in hours. |



| Column                     | Approximate meaning                                                                                                                                                               |
| -------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| equivalent_full_cycles     | Cumulative cycling wear expressed as full 0–100% charge–discharge equivalents. Partial cycles are normalized; e.g., two 50% discharges approximate one full cycle. technav.ieee+1 |

| soc_start_pct              | State of charge at the beginning of the cycle: remaining charge as a percentage of rated capacity. pmc.ncbi.nlm.nih+1                                                             |

| soc_end_pct                | State of charge at the end of the cycle.                                                                                                                                          |

| depth_of_discharge_pct     | How deeply the battery was discharged during the cycle; here approximately soc_start_pct - soc_end_pct. Deeper discharge generally adds more cycling stress. technav.ieee+1       |

| high_soc_exposure_fraction | Fraction of the cycle spent at high SOC, where the battery may experience elevated aging stress.                                                                                  |

| low_soc_exposure_fraction  | Fraction of the cycle spent at low SOC.                                                                                                                                           |
| charge_c_rate              | Charging speed normalized to battery capacity. A 1C rate would nominally charge the full capacity in one hour; 0.35C is relatively gentle. pmc.ncbi.nlm.nih                       |

| discharge_c_rate           | Discharge speed normalized to capacity; higher values mean a heavier electrical load.                                                                                             |

| charge_current_a           | Average or representative charging current in amperes.                                                                                                                            |

| discharge_current_a        | Average or representative discharging current in amperes.                                                                                                                         |

| charge_duration_min        | Duration of the charging portion, in minutes.                                                                                                                                     |

| discharge_duration_min     | Duration of the discharging portion, in minutes.                                                                                                                                  |

| energy_discharged_kwh      | Electrical energy delivered during discharge, in kilowatt-hours.                                                                                                                  |


| Column                     | Approximate meaning                                                                                                                          |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| ambient_temp_c             | Temperature of the surrounding environment, in °C.                                                                                           |
| pack_temp_c                | Temperature measured on or within the battery pack, in °C.                                                                                   |
| cumulative_high_temp_hours | Total accumulated time the pack has spent above a defined high-temperature threshold. Heat is a major degradation driver. pmc.ncbi.nlm.nih+1 |
| cooling_active             | Binary indicator of whether active cooling was operating during the cycle: typically 1 = yes, 0 = no.                                        |
| pack_voltage_mean_v        | Average pack voltage across the cycle, in volts.                                                                                             |
| pack_voltage_charge_v      | Representative or average pack voltage during charging, in volts.                                                                            |
| pack_voltage_discharge_v   | Representative or average pack voltage during discharge, in volts. Discharge voltage usually falls as load and internal resistance increase. |


| Column                   | Approximate meaning                                                                                                                                                                                  |
| ------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| state_of_health_pct      | SOH: current usable capacity or performance relative to the battery’s original condition. It generally declines from near 100% with aging. pmc.ncbi.nlm.nih+1                                        |
| eol_reached              | Whether the battery has reached its end-of-life criterion. For many lithium-ion applications, EOL is around 80% capacity retention, though datasets can use different thresholds. pmc.ncbi.nlm.nih+1 |
| remaining_useful_cycles  | Estimated number of additional charge–discharge cycles before EOL; a form of remaining useful life (RUL). pmc.ncbi.nlm.nih                                                                           |
| remaining_useful_efc     | Estimated remaining life measured in equivalent full cycles rather than raw cycle count.                                                                                                             |
| degradation_status       | Categorical health label, such as Normal, likely derived from SOH, resistance, or degradation-rate rules.                                                                                            |
| internal_resistance_mOhm | Internal resistance in milliohms. It typically rises as a lithium-ion battery ages and can cause greater voltage drop and heat generation under load. pmc.ncbi.nlm.nih+1                             |



one row in dataset = one recorded charge-discharge cycle, starting at soc_start_pct and ending at soc_end_pct

