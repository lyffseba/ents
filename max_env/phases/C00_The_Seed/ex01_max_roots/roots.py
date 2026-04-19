import onnx
from onnx import helper, TensorProto
from max import engine, driver
import numpy as np

def create_onnx():
    weights = np.array([
        [ 0.1,  0.2,  0.3,  0.4],
        [-0.1, -0.2, -0.3, -0.4],
        [ 0.5, -0.2,  0.8,  0.1]
    ], dtype=np.float32)
    
    weight_init = helper.make_tensor(
        name='embedding_weights',
        data_type=TensorProto.FLOAT,
        dims=weights.shape,
        vals=weights.flatten().tolist()
    )
    
    X = helper.make_tensor_value_info('input', TensorProto.INT64, [1])
    Y = helper.make_tensor_value_info('output', TensorProto.FLOAT, [1, 4])
    
    node = helper.make_node('Gather', inputs=['embedding_weights', 'input'], outputs=['output'], axis=0)
    graph = helper.make_graph(nodes=[node], name='EmbeddingGraph', inputs=[X], outputs=[Y], initializer=[weight_init])
    model = helper.make_model(graph, producer_name='ents_moulinette')
    
    onnx.save(model, 'soil.onnx')

def main():
    create_onnx()
    session = engine.InferenceSession(devices=driver.load_devices(driver.scan_available_devices()))
    model = session.load('soil.onnx')
    
    input_tensor = np.array([2], dtype=np.int64)
    out = model.execute(input=input_tensor)
    
    print(out['output'])

if __name__ == "__main__":
    main()
