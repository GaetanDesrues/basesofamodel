import logging

from basesofamodel.base_model import BaseScene


class MecaScene(BaseScene):
    def init(self):
        self.root.addObject("RequiredPlugin", pluginName="CardiacMeshTools")
        self.root.addObject("RequiredPlugin", pluginName="MechanicalHeart")

        self.build_meca_node()
        self.build_coupling_node()

    def build_meca_node(self):
        node = self.root.addChild("MecaNode")

        node.addObject(
            "CardiacVTKLoader",
            name="loader",
            TetraTriangle="Tetra",
            unitTime="ms",
            filename=self.ra("MESH_PATH"),
            FileFacetFiber=self.ra("FIBERS_PATH"),
            startContraction=float(self.ra("EM_DELAY"))
            + float(self.ra("START_CONTRACTION")),
            FileStiffnessParameters=self.ra("STIFFNESS_FILE"),
            FileContractionParameters=self.ra("CONTRACTION_FILE"),
            ElectroFile=self.ra("ELECTRO_FILE"),
            FileTetraConductivity=self.ra("CONDUCTIVITY_FILE"),
            TetraZoneName=self.ra("TETRA_ZONE_NAME"),
        )

        node.addObject(
            "EulerImplicitSolver",
            name="meca_solver",
            tags="meca",
            rayleighStiffness=self.ra("RAY_STIFF"),
            rayleighMass=self.ra("RAY_MASS"),
            firstOrder=self.ra("EULER_FIRST_ORDER"),
        )

        node.addObject(
            "CGLinearSolver",
            name="linear_solver",
            iterations="200",
            tags="meca",
            threshold="1e-12",
            tolerance="1e-12",
            template="GraphScattered",
        )
        node.addObject(
            "MechanicalObject",
            scale="1e-3",
            name="mecaObj",
            template="Vec3d",
            tags="meca",
            position="@loader.position",
            restScale="1",
        )

        node.addObject(
            "TetrahedronSetTopologyContainer",
            name="ContainerTetra",
            tetrahedra="@loader.tetrahedra",
            triangles="@loader.triangles",
            tags="meca",
        )
        node.addObject("TetrahedronSetTopologyModifier", name="Modifier")
        node.addObject(
            "TetrahedronSetGeometryAlgorithms", name="GeomAlgo", template="Vec3d"
        )

        # node.addObject("", )
        costa_params = f"{self.ra('costa_a')} {self.ra('costa_k')} 33.27 12.92 20.83 11.99 11.46 2.63"
        node.addObject(
            "CostaForceField",
            ParameterSet=costa_params,
            # ParameterSet="5000000 1428570 1 1 1 1 1 1",
            # a kappa bff bfs bss bfn bsn bnn
            fiberDirections="@loader.facetFibers",
            matrixRegularization="true",
            # ParameterSet="@loader.StiffnessParameters",
            name="MR_FF",
            tags="meca",
            # matrixRegularization="1",
            # depolarisationTimes="@loader.depoTimes",
            # APD="@loader.APDTimes",
            template="Vec3d",
            # activeRelaxation=self.ra("ACTIVE_RELAXATION"],)            # MaxPeakActiveRelaxation=self.ra("MAX_PEAK"],)            file=self.ra("JACFILE"),
        )
        node.addObject(
            "ContractionForceField",
            fiberDirections="@loader.facetFibers",
            addElastometry=True,
            name="contraction",
            tags="meca",
            useCoupling=True,
            tagContraction="tagContraction",
            APD="@loader.APDTimes",
            template="Vec3d",
            tetraContractivityParam="@loader.ContractionParameters",
            depolarisationTimes="@loader.depoTimes",
            viscosityParameter=self.ra("MU"),
            elasticModulus=self.ra("EEE"),
            file=self.ra("JACFILE3"),
            heartPeriod=self.ra("HEART_PERIOD"),
            # calculateStress=True,
            # SecSPK_passive="@MR_FF.MRStressPK",
            stressFile=self.ra("stressFile_ContractionForceField"),
        )
        node.addObject(
            "BaseConstraintForceField",
            name="String_Rings",
            # temporaryForce="True",   # False is default
            loadername="VTK",
            useForce="1",
            template="Vec3d",
            tags="meca",
            Zone=self.ra("RINGS_ZONE"),
            kp=self.ra("ATRIUM_FORCE"),
            kn=self.ra("ATRIUM_FORCE"),
            heartPeriod=self.ra("HEART_PERIOD"),
            normal="0 0 1",  # self.geoData["AxisHeart"],
            temporaryTimes=assoc(self.ra, "T_0L", "T_1L", "T_2L"),
        )
        node.addObject(
            "PressureConstraintForceField",
            DisableFirstAtriumContraction="false",
            template="Vec3d",
            name="pressureforceR",
            tags="meca",
            loadername="VTK",
            # windkessel="4",
            windkessel=self.ra("WK_order"),
            useProjection="1",
            Kiso=assoc(self.ra, "KISOR", "KISOR"),
            trianglesSurf="@loader.trianglesSurf",
            pointZoneName="@loader.pointZoneNames",
            loaderZoneNames="@loader.surfaceZoneNames",
            loaderZones="@loader.surfaceZones",
            pointZones="@loader.pointZones",
            SurfaceZone=self.ra("RV_ENDO_ZONE"),
            ZoneType=self.ra("ZONE_TYPE_PRESSURE"),  # Triangles or Points
            Pv0=self.ra("PV0R"),
            file=self.ra("RIGHT_PRESSURE_FILE"),
            heartPeriod=self.ra("HEART_PERIOD"),
            atriumParam=assoc(
                self.ra, "KatR", "Pat1R", "Pat2R", "V1R", "V2R", "T_0R", "T_1R", "T_2R"
            ),
            aorticParam=assoc(
                self.ra, "KarR", "Par1R", "Par2R", "TAUR", "RpR", "ZcR", "LLR"
            ),
            # EdgesOnBorder=edges["RV"],
            BoundaryEdgesPath=self.ra("BOUNDARY_EDGES_JSON"),
            BoundaryEdgesKey="RV",
            tolerance=self.ra("TOLERANCE_ISO"),
            loader_link="@loader",
            # contraction_forcefield="@contraction",
            # tetra_topology="@ContainerTetra",
            # strain="@strainMonitor",
            # escalier_pat=self.ra("ESCALIER"],)            # init_phase=0,
        )
        node.addObject(
            "PressureConstraintForceField",
            DisableFirstAtriumContraction="false",
            template="Vec3d",
            name="pressureforceL",
            tags="meca",
            loadername="VTK",
            # windkessel="4",
            windkessel=self.ra("WK_order"),  # 3
            useProjection="1",
            Kiso=assoc(self.ra, "KISOL", "KISOL"),
            trianglesSurf="@loader.trianglesSurf",
            pointZoneName="@loader.pointZoneNames",
            pointZones="@loader.pointZones",
            loaderZoneNames="@loader.surfaceZoneNames",
            loaderZones="@loader.surfaceZones",
            SurfaceZone=self.ra("LV_ENDO_ZONE"),
            ZoneType=self.ra("ZONE_TYPE_PRESSURE"),  # Triangles or Points
            Pv0=self.ra("PV0L"),
            file=self.ra("LEFT_PRESSURE_FILE"),
            file2=self.ra("LEFT_PRESSURE_FILE_2"),
            heartPeriod=self.ra("HEART_PERIOD"),
            atriumParam=assoc(
                self.ra, "KatL", "Pat1L", "Pat2L", "V1L", "V2L", "T_0L", "T_1L", "T_2L"
            ),  # Kat, Pat0, Patm, alpha1, alpha2, tof, tm, tc
            aorticParam=assoc(
                self.ra, "KarL", "Par1L", "Par2L", "TAUL", "RpL", "ZcL", "LLL"
            ),  # Kar, Par0, Pve, tau, Rp, Zc, L
            # EdgesOnBorder=edges["LV"],
            BoundaryEdgesPath=self.ra("BOUNDARY_EDGES_JSON"),
            BoundaryEdgesKey="LV",
            tolerance=self.ra("TOLERANCE_ISO"),
            loader_link="@loader",
            # contraction_forcefield="@contraction",
            # tetra_topology="@ContainerTetra",
            # strain="@strainMonitor.strain",
            # escalier_pat=self.ra("ESCALIER"],)            # init_phase=0,
        )
        node.addObject(
            "ContractionInitialization",
            name="InitializationContraction",
            template="ContractionInitialization<Vec3d,Vec3d>",
            tags="meca",
        )
        node.addObject(
            "ProjectivePressureConstraint",
            FFNames="pressureforceR pressureforceL",
            # forcefields="@pressureforceR @pressureforceL",
            # linear_solver="@linear_solver",
            name="project",
            template="Vec3d",
            tags="meca",
            file=self.ra("PROJECTIVE_PRESSURE_FILE"),
            optimiser=False,
            # vents_file=self.ra("VENTS_FILE")
        )
        node.addObject(
            "DiagonalMass",
            name="DiagonalMass",
            # template="Vec3d",
            tags="meca",
            massDensity=self.ra("MYO_DENSITY"),
        )
        node.addObject(
            "CardiacSimulationExporter",
            Tetras="1",
            ExportScale="1e3",
            name="VtkExporter",
            ExportFileType=".vtk",
            ExportEveryNSteps=self.ra("EXPORT_STEP"),
            Filename=self.ra("MESH_EXPORTED"),
            ExportStartStep=self.ra("START_EXPORT_STEP"),
            ExportSigmaC=False,
            ExportEc=False,
            ExportE1d=False,
            # exportVelocity=1,
            # exportAcceleration=1,
            contraction_forcefield="@contraction",
        )

    def build_coupling_node(self):
        node = self.root.addChild("Coupling")
        node.addObject(
            "EulerImplicitSolver",
            firstOrder="true",
            tags="tagContraction",
            rayleighStiffness="0",
            # template="Vec3d",
            rayleighMass="0",
        )
        node.addObject("Gravity", gravity="0 0 0", tags="tagContraction")
        node.addObject(
            "CGLinearSolver",
            name="linear-solver-coupling",
            template="GraphScattered",
            tags="tagContraction",
        )
        node.addObject(
            "MechanicalObject",
            position="@../MecaNode/InitializationContraction.outputs",
            name="contractObj",
            template="Vec3d",
            tags="tagContraction",
        )
        node.addObject(
            "ContractionCouplingForceField",
            StarlingEffect=False,  # "if used with verdandi"
            withFile=True,
            tetraContractivityParam="@../MecaNode/loader.ContractionParameters",
            tags="tagContraction",
            useSimple=False,  # If the model should be simplified
            depolarisationTimes="@../MecaNode/loader.depoTimes",
            APD="@../MecaNode/loader.APDTimes",
            alpha=self.ra("ALPHA"),
            n0=self.ra("F_N0"),
            n1=self.ra("F_N1"),
            n2=self.ra("F_N2"),
            file=self.ra("JACFILE2"),
        )
        node.addObject(
            "UniformMass",
            vertexMass="1",
            # template="Vec3d",
            tags="tagContraction",
        )


# Helper to concatenate params as x[args1]+' '+x[args2]+' '+...
def assoc(x, *args):
    return " ".join(str(s) for s in map(x.__call__, args))


log = logging.getLogger(__name__)
