import pickle
import tensorflow as tf
import numpy as np

tf.flags.DEFINE_boolean("allow_soft_placement", True, "Allow device soft device placement")
tf.flags.DEFINE_boolean("log_device_placement", False, "Log placement of ops on devices")
tf.flags.DEFINE_integer("batch_size", 1, "Batch Size (default: 1)")
tf.flags.DEFINE_string("checkpoint_dir", "", "Checkpoint directory from training run")
FLAGS = tf.flags.FLAGS
FLAGS._parse_flags()

print("Loading data...")
with open('./data/preprocessing/vocab.pkl', 'rb') as f:
    vocabulary = pickle.load(f)
with open('./data/preprocessing/vocab.pkl', 'rb') as f:
    vocabulary_inv = pickle.load(f)
print("Vocabulary size: {:d}".format(len(vocabulary)))

traindata = np.load('./data/preprocessing/validateX.npy')

checkpoint_file = "./data/runs/1462215568/checkpoints/model-246092"
graph = tf.Graph()
with graph.as_default():
    session_conf = tf.ConfigProto(
      allow_soft_placement=FLAGS.allow_soft_placement,
      log_device_placement=FLAGS.log_device_placement)
    sess = tf.Session(config=session_conf)
    with sess.as_default():
        # Load the saved meta graph and restore variables
        saver = tf.train.import_meta_graph("{}.meta".format(checkpoint_file))
        saver.restore(sess, checkpoint_file)

        # Get the placeholders from the graph by name
        input_x = graph.get_operation_by_name("input_x").outputs[0]
        # input_y = graph.get_operation_by_name("input_y").outputs[0]
        dropout_keep_prob = graph.get_operation_by_name("dropout_keep_prob").outputs[0]

        # Tensors we want to evaluate
        predictions = graph.get_operation_by_name("output/predictions").outputs[0]

        # Collect the predictions here
        all_predictions = []
        id = 1
        for row in traindata:
            if id % 100 == 0:
                print("done tweets: {:d}".format(id))
            prediction = sess.run(predictions, {input_x: [row], dropout_keep_prob: 1.0})[0]
            all_predictions.append((id, prediction))
            id += 1

        print("Prediction done")
        print("Writing predictions to file...")
        filename = "./data/output/prediction_cnn_1462215568.csv"
        submission = open(filename, 'w+')
        print('Id,Prediction', file=submission)
        for id, pred in all_predictions:
            if pred == 0:
                print("%d,-1" % id,file=submission)
            else:
                print("%d,1" % id,file=submission)
        print("...done.")