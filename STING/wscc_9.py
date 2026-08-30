# -------------------------------------------------------
# Import libraries and components
# -------------------------------------------------------
from sting.system import System
from sting.generator import VoltageSource4A, GFMI18A, GFLI16A
from sting.line import LinePiModel
from sting.bus import Bus
from sting.load import Load
from sting.timescales import Timepoint
from sting.utils.tuning import line_ieeerts79

# -------------------------------------------------------
# Definition of the WSCC 9-bus System
# -------------------------------------------------------

def wscc_9(case_directory=None):
    # Timepoint
    t1 = Timepoint(name="t1", weight=1)

    # Buses
    bus_1 = Bus(name="bus_1", zone="external", base_power_MVA=100, base_voltage_kV=230, base_frequency_Hz=60, minimum_voltage_pu=0.95, maximum_voltage_pu=1.05)
    bus_2 = Bus(name="bus_2", zone=None, base_power_MVA=100, base_voltage_kV=230, base_frequency_Hz=60, minimum_voltage_pu=0.95, maximum_voltage_pu=1.05)
    bus_3 = Bus(name="bus_3", zone="external", base_power_MVA=100, base_voltage_kV=230, base_frequency_Hz=60, minimum_voltage_pu=0.95, maximum_voltage_pu=1.05)
    bus_4 = Bus(name="bus_4", zone="external", base_power_MVA=100, base_voltage_kV=230, base_frequency_Hz=60, minimum_voltage_pu=0.95, maximum_voltage_pu=1.05)
    bus_5 = Bus(name="bus_5", zone="external", base_power_MVA=100, base_voltage_kV=230, base_frequency_Hz=60, minimum_voltage_pu=0.95, maximum_voltage_pu=1.05)
    bus_6 = Bus(name="bus_6", zone="external", base_power_MVA=100, base_voltage_kV=230, base_frequency_Hz=60, minimum_voltage_pu=0.95, maximum_voltage_pu=1.05)
    bus_7 = Bus(name="bus_7", zone="external", base_power_MVA=100, base_voltage_kV=230, base_frequency_Hz=60, minimum_voltage_pu=0.95, maximum_voltage_pu=1.05)
    bus_8 = Bus(name="bus_8", zone="external", base_power_MVA=100, base_voltage_kV=230, base_frequency_Hz=60, minimum_voltage_pu=0.95, maximum_voltage_pu=1.05)
    bus_9 = Bus(name="bus_9", zone="external", base_power_MVA=100, base_voltage_kV=230, base_frequency_Hz=60, minimum_voltage_pu=0.90, maximum_voltage_pu=1.5)

    # Loads
    load_1 = Load(bus="bus_5", zone="external", timepoint="t1", load_MW=90, load_MVAR=12)
    load_2 = Load(bus="bus_7", zone="external", timepoint="t1", load_MW=50, load_MVAR=4)
    load_3 = Load(bus="bus_9", zone="external", timepoint="t1", load_MW=100, load_MVAR=18)


    # Transmission Lines
    line_1_4 = LinePiModel(
        name="line_1_4", from_bus="bus_1", to_bus="bus_4", zone="external", base_power_MVA=100, base_voltage_kV=230, base_frequency_Hz=60, r_pu=0, x_pu=0.0576, g_pu=0, b_pu=0)
    line_4_5 = LinePiModel(
        name="line_4_5", from_bus="bus_4", to_bus="bus_5", zone="external", base_power_MVA=100, base_voltage_kV=230, base_frequency_Hz=60, r_pu=0.017, x_pu=0.092, g_pu=0, b_pu=0.158)
    line_5_6 = LinePiModel(
        name="line_5_6", from_bus="bus_5", to_bus="bus_6", zone="external", base_power_MVA=100, base_voltage_kV=230, base_frequency_Hz=60, r_pu=0.039, x_pu=0.17, g_pu=0, b_pu=0.358)
    line_3_6 = LinePiModel(
        name="line_3_6", from_bus="bus_3", to_bus="bus_6", zone="external", base_power_MVA=100, base_voltage_kV=230, base_frequency_Hz=60, r_pu=0, x_pu=0.0586, g_pu=0, b_pu=0)
    line_6_7 = LinePiModel(
        name="line_6_7", from_bus="bus_6", to_bus="bus_7", zone="external", base_power_MVA=100, base_voltage_kV=230, base_frequency_Hz=60, r_pu=0.0119, x_pu=0.1008, g_pu=0, b_pu=0.209)
    line_7_8 = LinePiModel(
        name="line_7_8", from_bus="bus_7", to_bus="bus_8", zone="external", base_power_MVA=100, base_voltage_kV=230, base_frequency_Hz=60, r_pu=0.0085, x_pu=0.072, g_pu=0, b_pu=0.149)
    line_8_2 = LinePiModel(
        name="line_8_2", from_bus="bus_8", to_bus="bus_2", zone=None, base_power_MVA=100, base_voltage_kV=230, base_frequency_Hz=60, r_pu=0.001, x_pu=0.5, g_pu=0, b_pu=0)
    line_8_9 = LinePiModel(
        name="line_8_9", from_bus="bus_8", to_bus="bus_9", zone="external", base_power_MVA=100, base_voltage_kV=230, base_frequency_Hz=60, r_pu=0.032, x_pu=0.161, g_pu=0, b_pu=0.306)
    line_9_4 = LinePiModel(
        name="line_9_4", from_bus="bus_9", to_bus="bus_4", zone="external", base_power_MVA=100, base_voltage_kV=230, base_frequency_Hz=60, r_pu=0.01, x_pu=0.085, g_pu=0, b_pu=0.176)

    # Add resistance and susceptance to lines based on typical values per mile for 230 kV lines to avoid zero values. The typical values are based on the IEEE RTS-79 test system.
    typical_parameters_per_mile = line_ieeerts79(base_voltage_kv=230, miles=1) 
    r_pu_mile = typical_parameters_per_mile["r_pu"]
    x_pu_mile = typical_parameters_per_mile["x_pu"]
    b_pu_mile = typical_parameters_per_mile["b_pu"]

    for line in [line_1_4, line_4_5, line_5_6, line_3_6, line_6_7, line_7_8, line_8_2, line_8_9, line_9_4]:

        estimated_miles = line.x_pu / x_pu_mile
        if line.r_pu == 0:
            line.r_pu = r_pu_mile * estimated_miles
            # print(f"Estimated r_pu for {line.name}: {line.r_pu:.6f}")

        if line.b_pu == 0:
            line.b_pu = b_pu_mile * estimated_miles
            # print(f"Estimated b_pu for {line.name}: {line.b_pu:.6f}")

        if line.b_pu > 0:
            line.g_pu = line.b_pu * 0.01
            # print(f"Estimated g_pu for {line.name}: {line.g_pu:.6f}")


    # Generation
    source = VoltageSource4A(
        name="grid", bus="bus_1", zone="external",
        minimum_active_power_MW=-200, maximum_active_power_MW=200, minimum_reactive_power_MVAR=-500, maximum_reactive_power_MVAR=500,
        cost_variable_USDperMWh=0, base_power_MVA=100, base_voltage_kV=230, base_frequency_Hz=60,
        r_pu=0.001, x_pu=0.005
    )

    gfmi_1 = GFMI18A(
        name="gfmi_2", bus="bus_2", zone=None,
        # Power flow 
        minimum_active_power_MW=120, maximum_active_power_MW=140, minimum_reactive_power_MVAR=-100, maximum_reactive_power_MVAR=100,
        cost_variable_USDperMWh=10, base_power_MVA=100, base_voltage_kV=0.48, base_frequency_Hz=60,
        # LCL filter
        rf1_pu=0.005, xf1_pu=0.15, csh_pu=0.066, rsh_pu=100,
        txr_power_MVA=100, txr_voltage1_kV=0.48, txr_voltage2_kV=230, txr_r1_pu=0.01, txr_x1_pu=0.1, txr_r2_pu=0.02, txr_x2_pu=0.1, 
        # Inner voltage controller
        kp_vc_pu=5, ki_vc_puHz=500, kffi_vc=0,
        # Inner current controller
        kp_cc_pu=4.77, ki_cc_puHz=60, kffv_cc=0,
        # Virtual inertia
        h_s=0.15, kd_pu=0.1, 
        # Voltage droop
        k_q_pu=0.05, w_q_puHz=2000
    )

    gfmi_2 = GFMI18A(
        name="gfmi_2", bus="bus_3", zone="external",
        # Power flow 
        minimum_active_power_MW=200, maximum_active_power_MW=250, minimum_reactive_power_MVAR=-100, maximum_reactive_power_MVAR=100,
        cost_variable_USDperMWh=10, base_power_MVA=100, base_voltage_kV=0.48, base_frequency_Hz=60,
        # LCL filter
        rf1_pu=0.005, xf1_pu=0.15, csh_pu=0.066, rsh_pu=100,
        txr_power_MVA=100, txr_voltage1_kV=0.48, txr_voltage2_kV=230, txr_r1_pu=0.01, txr_x1_pu=0.1, txr_r2_pu=0.02, txr_x2_pu=0.1, 
        # Inner voltage controller
        kp_vc_pu=0.562, ki_vc_puHz=484.989, kffi_vc=0.80,
        # Inner current controller
        kp_cc_pu=4.77, ki_cc_puHz=60, kffv_cc=0,
        # Virtual inertia
        h_s=2, kd_pu=70, 
        # Voltage droop
        k_q_pu=0.05, w_q_puHz=100
    )


    gfli_1 = GFLI16A(
        name="gfli_1", bus="bus_5", zone="external",
        # Power flow 
        minimum_active_power_MW=50, maximum_active_power_MW=100, minimum_reactive_power_MVAR=-100, maximum_reactive_power_MVAR=100,
        cost_variable_USDperMWh=10, base_power_MVA=100, base_voltage_kV=0.48, base_frequency_Hz=60,
        # LCL filter
        rf1_pu=0.002, xf1_pu=0.07, csh_pu=0.01, rsh_pu=100, 
        txr_power_MVA=100, txr_voltage1_kV=0.48, txr_voltage2_kV=230, txr_r1_pu=0.003/2, txr_x1_pu=0.08/2, txr_r2_pu=0.003/2, txr_x2_pu=0.08/2, 
        # Phase-locked loop (PLL)
        kp_pll_rad_s=100, ki_pll_rad2_s2=2500, tau_pll_s=1/100,
        # Inner current controller
        kp_cc_pu=0.05, ki_cc_puHz=0.6, kff_cc=0.75,
        # Power controllers
        kp_pc_pu=0.1, ki_pc_puHz=100
    )

    
    buses = [bus_1, bus_2, bus_3, bus_4, bus_5, bus_6, bus_7, bus_8, bus_9]
    timepoints = [t1]
    loads = [load_1, load_2, load_3]
    lines = [line_1_4, line_4_5, line_5_6, line_3_6, line_6_7, line_7_8, line_8_2, line_8_9, line_9_4]
    generators = [source, gfmi_1, gfmi_2, gfli_1]

    # Build grid model
    system = System(case_directory=case_directory)
    
    for component in buses + timepoints + loads + lines + generators:
        system.add(component)

    system.apply("post_system_init", system)

    return system
