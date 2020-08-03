from gql import gql


get_sessions = gql('''
query GetSessions {
    sessions {
        sessionId
    }
}
''')

with open("documents/EndSession.graphql") as f:
    end_session = gql(f.read())

with open("documents/CreateAllAndStartSession.graphql") as f:
    create_all_and_start_session = gql(f.read())

with open("documents/UpdateSoldier.graphql") as f:
    update_soldier = gql(f.read())

with open("documents/UpdateTarget.graphql") as f:
    update_target_twist = gql(f.read())

with open("documents/Subscriptions.graphql") as f:
    subscriptions = gql(f.read())