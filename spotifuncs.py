##imports

import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity

def create_df_from_API(api_results):
    """reads in the spotipy query results and returns a DataFrame"""
    track_name = []
    track_id = []
    artist = []
    album = []
    duration = []
    popularity = []
    for i, items in enumerate(api_results['items']):
            track_name.append(items['name'])
            track_id.append(items['id'])
            artist.append(items["artists"][0]["name"])
            duration.append(items["duration_ms"])
            album.append(items["album"]["name"])
            popularity.append(items["popularity"])

    # Create the final df   
    df = pd.DataFrame({ "track_name": track_name, 
                                "album": album, 
                                "track_id": track_id,
                                "artist": artist, 
                                "duration": duration, 
                                "popularity": popularity})

    return df



def append_audio_features(df,spotify_cred_manager, return_feat_df = False):
    """ Fetches the audio features for all songs in a DataFrame and
    appends these as rows to the DataFrame
    Requires spotipy to be set up with an auth token"""

    audio_features = spotify_cred_manager.audio_features(df["track_id"][:])
    assert len(audio_features) == len(df["track_id"][:])
    feature_cols = list(audio_features[0].keys())[:-7]
    features_list = []
    for features in audio_features:
            song_features = [features[col] for col in feature_cols]
            features_list.append(song_features)
    df_features = pd.DataFrame(features_list,columns = feature_cols)
    df = pd.concat([df,df_features],axis = 1)
    if return_feat_df == False:
        return df
    else:
        return df,df_features



def create_similarity_score(df,similarity_score = "linear"):
    features = list(df.columns[6:])
    df_features = df[features]
    df_features_scaled = StandardScaler().fit_transform(df_features)
    indices = pd.Series(df.index, index = df['track_name']).drop_duplicates()
    if similarity_score == "linear":
        linear_sim = linear_kernel(df_features_scaled, df_features_scaled)
        return linear_sim
    elif similarity_score == "cosine_sim":
        cosine_sim = cosine_similarity(df_features_scaled, df_features_scaled)
        return cosine_sim
    ##implement other measures

def get_recommendations(df,song_title, similarity_score = linear_sim):
    idx = indices[song_title]
    sim_scores = list(enumerate(similarity_score[idx]))
    sim_scores = sorted(sim_scores, key = lambda x: x[1],reverse = True)
    top_scores = sim_scores[1:6]
    song_indices = [i[0] for i in top_scores]
    return df["track_name"].iloc[song_indices]