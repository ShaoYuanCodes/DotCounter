import tensorflow as tf
import dot_input_manager as dim 

n_classes = 10
batch_size = 128
height = 28
width = 28
n_pixels = height*width

### CHANGE THIS TO SUIT YOUR SYSTEM
dotcounterdir = '/home/shao/Documents/DotCounter/'

### CHANGE THIS TO SELECT WHETHER YOU WANT TO INPUT MNIST OR DOT DATA
image_data = dotcounterdir + 'image_data/'
#image_data = dotcounterdir + 'mnist_image_data/'

dots = dim.read_data_sets(image_data, one_hot = True, num_classes = n_classes)

x = tf.placeholder('float', [None, int(n_pixels)])
y = tf.placeholder('float')

keep_rate = 0.8
keep_prob = tf.placeholder(tf.float32)


def conv2d(x, W):
    return tf.nn.conv2d(x, W, strides=[1,1,1,1], padding='SAME')

def maxpool2d(x):
    #                        size of window         movement of window
    return tf.nn.max_pool(x, ksize=[1,2,2,1], strides=[1,2,2,1], padding='SAME')



def convolutional_neural_network(x):
    weights = {'W_conv1':tf.Variable(tf.random_normal([2,2,1,32])),
               'W_conv2':tf.Variable(tf.random_normal([2,2,32,64])),
               'W_fc':tf.Variable(tf.random_normal([7*7*64,1024])),
               'out':tf.Variable(tf.random_normal([1024, n_classes]))}

    biases = {'b_conv1':tf.Variable(tf.random_normal([32])),
               'b_conv2':tf.Variable(tf.random_normal([64])),
               'b_fc':tf.Variable(tf.random_normal([1024])),
               'out':tf.Variable(tf.random_normal([n_classes]))}

    x = tf.reshape(x, shape=[-1, 28, 28, 1])

    conv1 = tf.nn.relu(conv2d(x, weights['W_conv1']) + biases['b_conv1'])
    conv1 = maxpool2d(conv1)
    
    conv2 = tf.nn.relu(conv2d(conv1, weights['W_conv2']) + biases['b_conv2'])
    conv2 = maxpool2d(conv2)

    fc = tf.reshape(conv2,[-1, 7*7*64])
    fc = tf.nn.relu(tf.matmul(fc, weights['W_fc'])+biases['b_fc'])
    fc = tf.nn.dropout(fc, keep_rate)

    output = tf.matmul(fc, weights['out'])+biases['out']

    return output

def train_neural_network(x):
    prediction = convolutional_neural_network(x)
    cost = tf.reduce_mean( tf.nn.softmax_cross_entropy_with_logits(prediction,y) )
    optimizer = tf.train.AdamOptimizer().minimize(cost)
    correct = tf.equal(tf.argmax(prediction, 1), tf.argmax(y, 1))
    accuracy = tf.reduce_mean(tf.cast(correct, 'float'))
    
    hm_epochs = 10
    saver = tf.train.Saver()
    with tf.Session() as sess:
        sess.run(tf.initialize_all_variables())

        for epoch in range(hm_epochs):
            epoch_loss = 0
            for _ in range(int(dots.train.num_examples/batch_size)):
                epoch_x, epoch_y = dots.train.next_batch(batch_size)
                _, c = sess.run([optimizer, cost], feed_dict={x: epoch_x, y: epoch_y})
                epoch_loss += c
                
            print('Epoch', epoch, 'completed out of',hm_epochs,'loss:',epoch_loss)
            print('Accuracy:',accuracy.eval({x:epoch_x, y:epoch_y}))
        
        for i in range(10):
            testSet = dots.test.next_batch(100)
            print('Test Set Accuracy:',accuracy.eval({x:testSet[0], y:testSet[1]}))

        save_path = saver.save(sess, (dotcounterdir + 'saved_nets/dots_net.ckpt'))
        print('Neural Net Variables Saved to Path: ', save_path)

        
train_neural_network(x)