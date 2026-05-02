import ProjectDescription

let project = Project(
    name: "{{ProjectName}}",
    organizationName: "{{OrganizationName}}",
    settings: .settings(
        base: [
            "DEVELOPMENT_TEAM": "{{DevelopmentTeam}}"
        ]
    ),
    targets: [
        .target(
            name: "{{ProjectName}}",
            destinations: .iOS,
            product: .app,
            bundleId: "{{BundleIdPrefix}}.{{ProjectName}}",
            infoPlist: .default,
            sources: ["Targets/{{ProjectName}}/Sources/**"],
            resources: ["Targets/{{ProjectName}}/Resources/**"],
            dependencies: []
        ),
        .target(
            name: "{{ProjectName}}Tests",
            destinations: .iOS,
            product: .unitTests,
            bundleId: "{{BundleIdPrefix}}.{{ProjectName}}Tests",
            infoPlist: .default,
            sources: ["Targets/{{ProjectName}}/Tests/**"],
            dependencies: [
                .target(name: "{{ProjectName}}")
            ]
        ),
    ]
)
