// --- Curve Nodes ---
CREATE (:Curve {name: "Shale Zone Cutoff", mnemonic: "GR_SH_CUT", type: "Cutoff", units: "API", source: "Create_Cutoff_Curve.htm"});
CREATE (:Curve {name: "C1", mnemonic: "C1", type: "User-defined", units: "ppm", source: "Create_Multiple_Curve_Data.htm"});
CREATE (:Curve {name: "C2", mnemonic: "C2", type: "User-defined", units: "ppm", source: "Create_Multiple_Curve_Data.htm"});
CREATE (:Curve {name: "Gamma Ray Table Curve", mnemonic: "GR_TAB", type: "Table", units: "API", source: "Create_Curve_Data_from_Table_Columns.htm"});
CREATE (:Curve {name: "Manual Polyline", mnemonic: "PL_MAN", type: "Polyline", units: "", source: "Create_Polyline_Curve.htm"});

// --- Operation Nodes ---
CREATE (:Operation {name: "Create User-defined Curve"});
CREATE (:Operation {name: "Create Cutoff Curve"});
CREATE (:Operation {name: "Create Curve From Table Columns"});
CREATE (:Operation {name: "Create Polyline Curve"});
CREATE (:Operation {name: "Create Multiple Curve Data"});
CREATE (:Operation {name: "Edit Curve Data"});
CREATE (:Operation {name: "Mouse Set Curve Data"});
CREATE (:Operation {name: "Compile Curves"});
CREATE (:Operation {name: "View and Edit Curve Groups"});
CREATE (:Operation {name: "Generate Integrated Travel Time Pips"});

// --- Group Nodes ---
CREATE (:Group {name: "Gas Components"});
